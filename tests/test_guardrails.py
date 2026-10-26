from rag.guardrails import asks_for_diagnosis, is_emergency


def test_emergency_is_detected():
    assert is_emergency("I have chest pain, what should I do?")


def test_normal_question_is_not_emergency():
    assert not is_emergency("What are the symptoms of dengue?")


def test_diagnosis_request_is_detected():
    assert asks_for_diagnosis("Do I have diabetes?")


def test_information_question_is_not_diagnosis():
    assert not asks_for_diagnosis("What are the types of diabetes?")