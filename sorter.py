class Sorter:
    def __init__(self, filters_score):
        self.filters_score = filters_score

    def calculate_relevance_score(self, resume):
        score = 0

        # Проверка должности
        if self.filters_score.get("job_position") and self.filters_score["job_position"].lower() in resume["title"].lower():
            score += 10  # Если должность подходит, добавляем 10 баллов

        # Проверка города
        if self.filters_score.get("city") and self.filters_score["city"].lower() in resume["Город"].lower():
            score += 5  # Если город подходит, добавляем 5 баллов

        # Проверка типа занятости
        if self.filters_score.get("employment_type") and self.filters_score["employment_type"].lower() in resume["Занятость"].lower():
            score += 5  # Если тип занятости подходит, добавляем 5 баллов

        # Проверка ключевых слов
        if self.filters_score.get("keywords"):
            score += sum(3 for keyword in self.filters_score["keywords"] if keyword and keyword.lower() in resume.get("Навыки", "").lower())

        # Оценка по опыту
        if self.filters_score.get("employment_type") and resume.get("Опыт") != "Опыт не найден":
            score += 5  # Добавляем 5 баллов за наличие опыта

        return score

    def sort_candidates(self, candidates):
        """Сортировка кандидатов по релевантности."""
        # Добавляем к каждому резюме баллы
        for candidate in candidates:
            candidate["score"] = self.calculate_relevance_score(candidate)

        # Сортируем по баллам
        return sorted(candidates, key=lambda x: x["score"], reverse=True)