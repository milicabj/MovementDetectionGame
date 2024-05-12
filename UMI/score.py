import json
import os

# score_file_path = "best_score.json"
# default_data = {"best": 0}

score_file_path = "best_scores.json"
default_data = {"best": []}
max_scores = 100  # Maximum number of scores to keep


class ScoreService:
    @staticmethod
    def create_score_file_if_not_exist() -> None:
        if os.path.exists(score_file_path):
            return

        ScoreService.update_score_file(default_data)

    @staticmethod
    def load_score_file() -> dict:
        with open(score_file_path, mode="r", encoding="utf-8-sig") as file:
            return json.loads(file.read())

    @staticmethod
    # def get_max_score() -> int:
    def get_top_scores(num_scores: int) -> list:
        ScoreService.create_score_file_if_not_exist()
        data = ScoreService.load_score_file()

        # return data.get("best")
        sorted_scores = sorted(data["best"], reverse=True)
        return sorted_scores[:num_scores]

    @staticmethod
    def update_score_file(data: dict):
        with open(score_file_path, mode="w", encoding="utf-8") as file:
            json.dump(data, file)

    # @staticmethod
    # def update_max_score(new_score):
    #     data = ScoreService.load_score_file()
    #     data["best"] = new_score
    #     ScoreService.update_score_file(data)

    @staticmethod
    def add_score(new_score: int) -> None:
        data = ScoreService.load_score_file()
        if new_score not in data["best"]:
            data["best"].append(new_score)
        # samo cuva odredjeni broj scorova u jsonu
        data["best"] = sorted(data["best"], reverse=True)[:max_scores]

        ScoreService.update_score_file(data)

    # @staticmethod
    # def update_max_scores(new_scores: list) -> None:
    #     data = ScoreService.load_score_file()
    #     data["best"] = new_scores
    #     ScoreService.update_score_file(data)

# top_scores = ScoreService.get_top_scores(5)
