import pytest

from bot import won
from bot import (
    CROSS, ZERO, FREE_SPACE as FREE
)


@pytest.mark.parametrize(
    "state,expected",
    [
        pytest.param(
            [
                [FREE, FREE, FREE],
                [FREE, FREE, FREE],
                [FREE, FREE, FREE]
            ],
            False,
        ),
        pytest.param(
            [
                [FREE, FREE, ZERO],
                [CROSS, CROSS, CROSS],
                [FREE, ZERO, FREE]
            ],
            True,
        ),
        pytest.param(
            [
                [FREE, FREE, CROSS],
                [ZERO, CROSS, CROSS],
                [CROSS, ZERO, FREE]
            ],
            True,
        ),
        pytest.param(
            [
                [FREE, CROSS, ZERO],
                [CROSS, ZERO, CROSS],
                [ZERO, CROSS, FREE]
            ],
            True,
        ),
        pytest.param(
            [
                [CROSS, ZERO, ZERO],
                [CROSS, CROSS, FREE],
                [ZERO, FREE, CROSS]
            ],
            True,
        ),
        pytest.param(
            [
                [CROSS, ZERO, ZERO],
                [CROSS, ZERO, FREE],
                [CROSS, FREE, CROSS]
            ],
            True,
        ),
        pytest.param(
            [
                [ZERO, FREE, FREE],
                [CROSS, ZERO, CROSS],
                [CROSS, CROSS, ZERO]
            ],
            True,
        ),
        pytest.param(
            [
                [ZERO, CROSS, CROSS],
                [ZERO, FREE, FREE],
                [ZERO, CROSS, CROSS]
            ],
            True,
        ),
        pytest.param(
            [
                [ZERO, ZERO, ZERO],
                [CROSS, FREE, CROSS],
                [CROSS, FREE, CROSS]
            ],
            True,
        ),
        pytest.param(
            [
                [ZERO, CROSS, CROSS],
                [CROSS, ZERO, ZERO],
                [CROSS, ZERO, CROSS]
            ],
            False,
        ),
    ],
)
def test_won_is_correct(state: list[list[str]], expected: bool):
    result = won(state)
    assert result == expected
