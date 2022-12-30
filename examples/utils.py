class CacheData:
    texts = []
    text_ids = []
    diagrams = []
    text_embeddings = []
    diagram_embeddings = []

    def append_text(self, text, text_id, question_id) -> None:
        text_dict = {}
        text_dict["textId"] = text_id
        text_dict["questionId"] = question_id
        text_dict["text"] = text
        self.__class__.texts.append(text_dict)

    def append_diagram(self, diagram, diagram_id, quesntion_id) -> None:
        diagrams_dict = {}
        diagrams_dict["diagramId"] = diagram_id
        diagrams_dict["questionId"] = quesntion_id
        diagrams_dict["diagram"] = diagram
        self.__class__.diagrams.append(diagrams_dict)

    def append_text_embedding(self, text_embedding) -> None:
        self.__class__.text_embeddings.append(text_embedding)

    def append_diagram_embedding(self, diagram_embedding) -> None:
        self.__class__.diagram_embeddings.append(diagram_embedding)

    def append_text_id(self, id):
        self.__class__.text_ids.append(id)
