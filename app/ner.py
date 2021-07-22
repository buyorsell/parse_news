from natasha import (
	Segmenter,
	MorphVocab,

	NewsEmbedding,
	NewsMorphTagger,
	# NewsSyntaxParser,
	NewsNERTagger,

	# NamesExtractor,

	Doc
)
import pandas as pd

segmenter = Segmenter()
morph_vocab = MorphVocab()

emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
# syntax_parser = NewsSyntaxParser(emb)
ner_tagger = NewsNERTagger(emb)

# names_extractor = NamesExtractor(morph_vocab)


def process_news(news):

	news['pers'] = []
	news['orgs'] = []
	news['locs'] = []

	doc = Doc(news['text'])
	doc.segment(segmenter)
	doc.tag_ner(ner_tagger)
	doc.tag_morph(morph_tagger)

	for span in doc.spans:

		span.normalize(morph_vocab)
		word_a = span.normal

		for word_b in news[span.type.lower() + 's']:

			if word_a in word_b:
				break

		else:

			news[span.type.lower() + 's'].append(word_a)

	return news