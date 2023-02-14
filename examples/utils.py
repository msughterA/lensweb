class CacheData:
    text_ids_map = {}
    text_embeddings = []
    text_ids = []

    def append_data(self, question_id, text_embedding):
        index = len(self.__class__.text_embeddings) - 1
        # text_dict = {
        #     'index':index,
        #     ''
        # }
        self.__class__.text_ids_map[str(question_id)] = index
        self.__class__.text_embeddings.append(text_embedding)
        self.__class__.text_ids.append(question_id)

    def edit_data(self, question_id, new_text_embedding):
        index = self.__class__.text_ids_map[str(question_id)]
        self.__class__.text_embeddings[index] = new_text_embedding

    def remove_data(self, question_id):
        index = self.__class__.text_ids_map[str(question_id)]
        del self.__class__.text_embeddings[index]
        del self.__class__.text_ids[index]
        del self.__class__.text_ids_map[question_id]

        # revaluate indices of the text embeddings in the text_ids_map
        for i, qid in enumerate(self.__class__.text_ids_map.keys()):
            self.__class__.text_ids_map[qid] = i
