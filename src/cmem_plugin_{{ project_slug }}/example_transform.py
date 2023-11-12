"""lifetime(age) transform plugin module"""
import datetime
from collections.abc import Sequence
from datetime import date

from cmem_plugin_base.dataintegration.description import (
    Plugin,
    PluginParameter,
)
from cmem_plugin_base.dataintegration.plugins import TransformPlugin


@Plugin(
    label="Lifetime (age - example from template)",
    description="From the input date,"
    "the value gets transformed into number of years (age)."
    " Supports only xsd:date(YYYY-MM-DD) format.",
    documentation="""
This example transform operator returns lifetime(age).

From the input date,
the value gets transformed into number of years(age).

Input Date:         2000-05-22
Current Date:       2022-08-19
Transformed Output: 22

The parameter can be specified:

- 'date': specify a date in xsd:date(yyyy-MM-dd) format
""",
    parameters=[
        PluginParameter(
            name="start_date",
            label="Date",
            description="specify a date to know its lifetime(age).",
            default_value=None,
        ),
    ],
)
class Lifetime(TransformPlugin):
    """Lifetime Transform Plugin"""

    DATE_FORMAT = "%Y-%m-%d"

    def __init__(self, start_date: str):
        self.start_date = start_date

    def transform(self, inputs: Sequence[Sequence[str]]) -> Sequence[str]:
        """Do the actual transformation of values"""
        result = []
        if len(inputs) != 0:
            for collection in inputs:
                result += [f"{self._calculate_age(_)}" for _ in collection]
        if len(result) == 0 and len(self.start_date) > 0:
            result += [f"{self._calculate_age(self.start_date)}"]
        return result

    def _calculate_age(self, value: str) -> int:
        """Calculate age in years"""
        today = date.today()  # noqa: DTZ011
        born = datetime.datetime.strptime(value, self.DATE_FORMAT).date()  # noqa: DTZ007
        try:
            birthday = born.replace(year=today.year)

        # raised when birthdate is February 29
        # and the current year is not a leap year
        except ValueError:
            birthday = born.replace(year=today.year, month=born.month + 1, day=1)

        if birthday > today:
            return today.year - born.year - 1

        return today.year - born.year
