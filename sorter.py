class Sorter:
    def __init__(self, filters_score):
        self.filters_score = filters_score

    def calculate_relevance_score(self, resume):
        score = 0

        # Проверяем каждый фильтр на пустоту
        if self.filters_score["job_position"]:
            if self.filters_score["job_position"].lower() in resume["title"].lower():
                score += 10  # Если должность подходит, добавляем 10 баллов

        if self.filters_score["city"]:
            if self.filters_score["city"].lower() in resume["Город"].lower():
                score += 5  # Если город подходит, добавляем 5 баллов

        if self.filters_score["employment_type"]:
            if self.filters_score["employment_type"].lower() in resume["Занятость"].lower():
                score += 5  # Если тип занятости подходит, добавляем 5 баллов

        # Для ключевых слов, если они есть в фильтре
        if self.filters_score["keywords"]:
            for keyword in self.filters_score["keywords"]:
                if keyword and keyword.lower() in resume["Навыки"].lower():
                    score += 3  # Добавляем 3 балла за каждое совпадение ключевого слова

        # Оценка по опыту (если опыт задан в фильтре)
        if self.filters_score["employment_type"] and resume.get("Опыт") != "Опыт не найден":
            score += 5  # Добавляем 5 баллов за наличие опыта

        return score

    def sort_candidates(self, candidates):
        """Сортировка кандидатов по релевантности."""
        # Добавляем к каждому резюме баллы
        for candidate in candidates:
            candidate["score"] = self.calculate_relevance_score(candidate)

        # Сортируем по баллам
        return sorted(candidates, key=lambda x: x["score"], reverse=True)
