import json
import time
from enum import Enum
from typing import Dict

import requests


class SoloonColor(Enum):
    BLUE = "blue"
    RED = "red"
    PURPLE = "purple"
    WHITE = "white"


class ComethDirection(Enum):
    UP = "up"
    DOWN = "down"
    RIGHT = "right"
    LEFT = "left"


class CrossMintBaseApi:
    session = requests.Session()
    base_url = "https://challenge.crossmint.io/api/"
    candidate_id = "175f45fe-b12d-4337-8723-1fb2c8cc8c60"
    headers = {"Content-Type": "application/json"}

    @classmethod
    def _parse_path(cls, path: str):
        return path.lstrip("/")

    @classmethod
    def _parse_response(cls, response: requests.Response):
        ret = response.json()
        if response.status_code != 200 or ret.get("error", False):
            print("*" * 100)
            print("ERROR RESPONSE: ", ret)
            print("*" * 100)
            raise Exception("Invalid response code")
        print(f"Response of {response.url}", ret)
        return ret

    @classmethod
    def _post(cls, path: str, data: Dict = None):
        ret = cls.session.post(
            f"{cls.base_url}{cls._parse_path(path)}",
            json=dict(**(data or {}), candidateId=cls.candidate_id),
        )
        print(f"POST {path} with data {json.dumps(data or {})}")
        return cls._parse_response(ret)

    @classmethod
    def _get(cls, path: str, data: Dict = None):
        ret = cls.session.get(
            f"{cls.base_url}{cls._parse_path(path)}",
            params=dict(candidateId=cls.candidate_id, **(data or {}))
        )
        print(f"GET {path} with data {json.dumps(data or {})}")
        return cls._parse_response(ret)

    @classmethod
    def _delete(cls, path: str, data: Dict = None):
        ret = cls.session.delete(
            f"{cls.base_url}{cls._parse_path(path)}",
            json=dict(**(data or {}), candidateId=cls.candidate_id),
        )
        print(f"GET {path} with data {json.dumps(data or {})}")
        return cls._parse_response(ret)


class PolyanetsApi(CrossMintBaseApi):
    @classmethod
    def create_polyanets(cls, row: int, column: int):
        return cls._post("/polyanets", data=dict(row=row, column=column))

    @classmethod
    def delete_polyanets(cls, row: int, column: int):
        return cls._delete("/polyanets", data=dict(row=row, column=column))


class SoloonsApi(CrossMintBaseApi):
    @classmethod
    def create_soloons(cls, row: int, column: int, color: SoloonColor):
        return cls._post("/soloons", data=dict(row=row, column=column, color=color.value))

    @classmethod
    def delete_soloons(cls, row: int, column: int):
        return cls._delete("/soloons", data=dict(row=row, column=column))


class ComethApi(CrossMintBaseApi):
    @classmethod
    def create_cometh(cls, row: int, column: int, direction: ComethDirection):
        return cls._post("/comeths", data=dict(row=row, column=column, direction=direction.value))

    @classmethod
    def delete_cometh(cls, row: int, column: int):
        return cls._delete("/comeths", data=dict(row=row, column=column))


class GoalMapApi(CrossMintBaseApi):
    @classmethod
    def get_goal(cls):
        ret = cls._get(f"/map/{cls.candidate_id}/goal")
        return ret["goal"]


def complete_phase1():
    start, end = 2, 8
    while start <= 8:
        PolyanetsApi.create_polyanets(start, start)
        if start != end:
            PolyanetsApi.create_polyanets(start, end)
        start += 1
        end -= 1


def create_node(name: str, x: int, y: int):
    if name == "POLYANET":
        PolyanetsApi.create_polyanets(x, y)
    elif name.endswith("SOLOON"):
        color = name.split("_")[0].lower()
        SoloonsApi.create_soloons(x, y, SoloonColor(color))
    elif name.endswith("COMETH"):
        direction = name.split("_")[0].lower()
        ComethApi.create_cometh(x, y, ComethDirection(direction))


def complete_phase2():
    goal = GoalMapApi.get_goal()
    for line_idx, line in enumerate(goal):
        for node_idx, node in enumerate(line):
            create_node(node, line_idx, node_idx)
        # To avoid rate limit
        print(f"Finish Line {line_idx + 1}... Sleep for 3 seconds...")
        time.sleep(3)


if __name__ == "__main__":
    complete_phase2()
