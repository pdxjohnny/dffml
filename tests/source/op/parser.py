import json


def parser(json_file: str) -> dict:
    with open(json_file) as f:
        parsed_data = {}
        data = json.load(f)["data"]
        for entry in data:
            title = entry["title"]
            for para in entry["paragraphs"]:
                context = para["context"]
                for qa in para["qas"]:
                    id = qa["id"]
                    question = qa["question"]
                    start_pos_char = None
                    answers = []
                    answer_text = None

                    if "is_impossible" in qa:
                        is_impossible = qa["is_impossible"]
                    else:
                        is_impossible = False
                    if not is_impossible:
                        answer = qa["answers"][0]
                        answer_text = answer["text"]
                        start_pos_char = answer["answer_start"]
                    parsed_data[id] = {
                        "features": {
                            "question": question,
                            "context": context,
                            "answer_text": answer_text,
                            "start_pos_char": start_pos_char,
                            "title": title,
                            "is_impossible": is_impossible,
                            "answers": answers,
                        }
                    }
        return parsed_data
