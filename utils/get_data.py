import json

from bs4 import BeautifulSoup

# Открываем локальный HTML-файл
with open("news_type.html", "r", encoding="utf-8") as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, "html.parser")

fixtures = []


# Функция для парсинга общего формата фильтров, где есть ul.filter_list и li>label>input
def parse_filter_block(soup, filter_class, model_name):
    data = []
    # Находим нужный блок по классу, например .filter_subregion_id
    filter_div = soup.select_one(f".{filter_class}")
    if not filter_div:
        return []
    # Извлекаем все чекбоксы
    checkboxes = filter_div.select("ul.filter_list li input[type=checkbox]")
    pk = 1
    for cb in checkboxes:
        data_id = cb.get("data-id")
        # Название находится в соседнем span.ttl
        ttl_span = cb.find_next("span", class_="ttl")
        name = ttl_span.get_text(strip=True) if ttl_span else ""

        # Формируем объект фикстуры
        data.append(
            {
                "model": model_name,
                "pk": pk,
                "fields": {"name": name, "param_value": data_id},
            }
        )
        pk += 1
    return data


def parse_news_type_block(soup, filter_class, model_name):
    filter_div = soup.select_one(f".{filter_class}")
    if not filter_div:
        return []
    items = filter_div.select("ul.select_wrapper li a.item")
    data = []
    pk = 1

    # Предположим следующую логику:
    # "Все новости" -> param_value = "0"
    # "Только важные" -> param_value = "1"
    # Если есть ещё пункты, можно добавить условия.

    for item in items:
        name = item.get_text(strip=True)
        if "Все" in name:
            param_value = "0"
        elif "важные" in name:
            param_value = "1"
        else:
            # Если появятся новые типы, нужно будет добавить логику или оставить пустым
            param_value = ""

        data.append(
            {
                "model": model_name,
                "pk": pk,
                "fields": {"name": name, "param_value": param_value},
            }
        )
        pk += 1

    return data


# Парсим регионы
regions_data = parse_filter_block(soup, "filter_subregion_id", "news.Region")
fixtures.extend(regions_data)

# Парсим языки
languages_data = parse_filter_block(soup, "filter_language", "news.Language")
fixtures.extend(languages_data)

# Парсим темы (NewsTheme)
themes_data = parse_filter_block(soup, "filter_section_id", "news.NewsTheme")
fixtures.extend(themes_data)

# Парсим страны (Country)
countries_data = parse_filter_block(soup, "filter_country_id", "news.Country")
fixtures.extend(countries_data)

news_types_data = parse_news_type_block(soup, "importantNews", "news.NewsType")
fixtures.extend(news_types_data)
# Важный момент: тип новостей (NewsType) может быть задан иначе (в виде select),
# в таком случае нужно отдельно спарсить их (если они присутствуют) или вручную занести.

# Сохраняем результат в JSON-файл
with open("filters_type.json", "w", encoding="utf-8") as out:
    json.dump(fixtures, out, ensure_ascii=False, indent=4)
