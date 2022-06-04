from typing import Any, Dict, Tuple
from types import FunctionType
from django.db.models import QuerySet
from django_extensions.management import jobs
from datetime import datetime, timedelta

from utils.helpers import log, not_naive_datetime


class AppJob(jobs.BaseJob):
    """
    Base class for all app jobs.
    """

    def __init__(
        self,
        job_method: str = "",
        job_args: Tuple[Any] = (),
        job_kwargs: Dict[str, Any] = {},
    ) -> None:
        self._job_method = job_method
        self._job_args = job_args
        self._job_kwargs = job_kwargs
        super().__init__()

    def run_with_log(
        self,
        msg: str = "",
        job: FunctionType = None,
        *job_args: Tuple[Any],
        **job_kwargs: Dict[str, Any],
    ):
        """
        Log the time of job.
        """
        d1 = datetime.now()
        job_result = None
        if callable(job):
            job_result = job(*job_args, **job_kwargs)
        log(
            "{} took time: {:.6f} secs.".format(
                msg, (datetime.now() - d1).total_seconds()
            ),
            "info",
        )
        return job_result

    def records_with_log(self, records: QuerySet):
        """
        Log the number of records.
        """
        records_len = 0
        if records:
            records_len = len(records)
        log(
            "{} Records were found from {} model.".format(
                records_len, records.model.__name__
            ),
            "info",
        )
        return records

    def execute(self):
        """
        Executing the job.
        """
        if not hasattr(self, self._job_method):
            raise NotImplementedError(
                "Job method `{}` is not provided.".format(self._job_method)
            )
        log("++++++++++++++++++++++++++++++++++", "info")
        log("Starting job execution", "info")
        log("++++++++++++++++++++++++++++++++++", "info")
        self.run_with_log(
            self.help,
            getattr(self, self._job_method)(*self._job_args, **self._job_kwargs),
        )
        log("Job executed successfully.", "info")
        log("++++++++++++++++++++++++++++++++++\n", "info")


class MinutelyJob(jobs.MinutelyJob, AppJob):
    def __init__(self) -> None:
        super().__init__(
            job_method=getattr(self, "_job_method", ""),
            job_args=getattr(self, "_job_args", ()),
            job_kwargs=getattr(self, "_job_kwargs", {}),
        )


class QuarterHourlyJob(jobs.QuarterHourlyJob, AppJob):
    def __init__(self) -> None:
        super().__init__(
            job_method=getattr(self, "_job_method", ""),
            job_args=getattr(self, "_job_args", ()),
            job_kwargs=getattr(self, "_job_kwargs", {}),
        )


class HourlyJob(jobs.HourlyJob, AppJob):
    def __init__(self) -> None:
        super().__init__(
            job_method=getattr(self, "_job_method", ""),
            job_args=getattr(self, "_job_args", ()),
            job_kwargs=getattr(self, "_job_kwargs", {}),
        )


class DailyJob(jobs.DailyJob, AppJob):
    def __init__(self) -> None:
        super().__init__(
            job_method=getattr(self, "_job_method", ""),
            job_args=getattr(self, "_job_args", ()),
            job_kwargs=getattr(self, "_job_kwargs", {}),
        )


class WeeklyJob(jobs.WeeklyJob, AppJob):
    def __init__(self) -> None:
        self._weekday = datetime.now().weekday()
        self._week_start = not_naive_datetime() - timedelta(days=7)
        super().__init__(
            job_method=getattr(self, "_job_method", ""),
            job_args=getattr(self, "_job_args", ()),
            job_kwargs=getattr(self, "_job_kwargs", {}),
        )


class MonthlyJob(jobs.MonthlyJob, AppJob):
    def __init__(self) -> None:
        self._month = datetime.now().month
        self._month_start = not_naive_datetime() - timedelta(days=30)
        super().__init__(
            job_method=getattr(self, "_job_method", ""),
            job_args=getattr(self, "_job_args", ()),
            job_kwargs=getattr(self, "_job_kwargs", {}),
        )


class YearlyJob(jobs.YearlyJob, AppJob):
    def __init__(self) -> None:
        super().__init__(
            job_method=getattr(self, "_job_method", ""),
            job_args=getattr(self, "_job_args", ()),
            job_kwargs=getattr(self, "_job_kwargs", {}),
        )
