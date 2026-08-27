import queue
import uuid
import concurrent.futures
import logging
from dataclasses import dataclass

import streamlit as st

from agents import fetch_seo_data, analysis_step, writing_step, agents


MAX_WORKERS = 4
logger = logging.getLogger(__name__)


@st.cache_resource(show_spinner=False)
def get_executor() -> concurrent.futures.ThreadPoolExecutor:
    """One shared thread pool per server process, reused across all sessions."""
    return concurrent.futures.ThreadPoolExecutor(
        max_workers=MAX_WORKERS,
        thread_name_prefix="capton-job",
    )


@dataclass
class Job:
    job_id: str
    future: concurrent.futures.Future
    progress_queue: "queue.Queue"
    script_preview: str = ""
    output_language: str = "English"


def _run_pipeline(
    script: str,
    output_language: str,
    progress_q: "queue.Queue",
) -> dict:
    """Runs entirely inside a worker thread."""

    def report(pct: int, message: str) -> None:
        progress_q.put((pct, message))

    try:
        report(10, "✅ Script received — initialising workflow…")

        # ---------------------------------------------------------
        # SEO
        # ---------------------------------------------------------
        report(20, "⏳ Fetching live SEO context…")

        seo_context = fetch_seo_data(script=script)

        # SEO is supplemental context, not a hard dependency.
        # fetch_seo_data() now returns a fallback context when
        # live search is unavailable.
        if not seo_context:
            seo_context = (
                "Live SEO context was unavailable. "
                "Infer SEO keywords and search intent directly "
                "from the supplied script."
            )
            logger.warning(
                "SEO context was empty; using pipeline fallback."
            )
            report(
                40,
                "⚠️ Live SEO unavailable — continuing with script context",
            )
        else:
            report(40, "✅ SEO context ready")

        # ---------------------------------------------------------
        # Agents
        # ---------------------------------------------------------
        analyzer, writer = agents()

        # ---------------------------------------------------------
        # Analysis
        # ---------------------------------------------------------
        report(
            55,
            "⏳ Analysing topic, audience, and emotion…",
        )

        analysis_result = analysis_step(
            script=script,
            seo_context=seo_context,
            analyzer=analyzer,
        )

        if not isinstance(analysis_result, dict) or "error" in analysis_result:
            err = (
                analysis_result.get("error", "Unknown")
                if isinstance(analysis_result, dict)
                else type(analysis_result).__name__
            )
            raise RuntimeError(f"Analysis failed: {err}")

        analysis = analysis_result.get("analysis", "")

        if not analysis:
            raise RuntimeError(
                "Analysis completed but returned empty text."
            )

        report(75, "✅ Analysis complete")

        # ---------------------------------------------------------
        # Writing
        # ---------------------------------------------------------
        report(
            85,
            f"⏳ Crafting hooks and captions in {output_language}…",
        )

        writing_result = writing_step(
            script=script,
            seo_context=seo_context,
            analysis=analysis,
            writer=writer,
            output_language=output_language,
        )

        if not isinstance(writing_result, dict) or "error" in writing_result:
            err = (
                writing_result.get("error", "Unknown")
                if isinstance(writing_result, dict)
                else "Invalid output."
            )
            raise RuntimeError(f"Writing failed: {err}")

        hooks = writing_result.get("hooks", [])
        caption = writing_result.get("caption", "")
        hashtags = writing_result.get("hashtags", [])

        if not hooks and not caption and not hashtags:
            raise RuntimeError("Writer returned empty outputs.")

        report(100, "✅ Content generation finished")

        return {
            "hooks": hooks,
            "caption": caption,
            "hashtags": hashtags,
        }

    except Exception as exc:
        logger.exception("Generation worker failed")
        progress_q.put(("error", str(exc)))
        raise


def submit_job(script: str, output_language: str) -> Job:
    """Submit a new pipeline run to the shared executor."""
    executor = get_executor()
    progress_q: "queue.Queue" = queue.Queue()

    logger.info(
        "Submitting generation job for %d characters",
        len(script),
    )

    future = executor.submit(
        _run_pipeline,
        script,
        output_language,
        progress_q,
    )

    return Job(
        job_id=str(uuid.uuid4()),
        future=future,
        progress_queue=progress_q,
        script_preview=script[:80],
        output_language=output_language,
    )


def drain_progress(job: Job) -> list:
    """Non-blocking read of every progress event queued so far."""
    events = []

    while True:
        try:
            events.append(job.progress_queue.get_nowait())
        except queue.Empty:
            break

    return events
