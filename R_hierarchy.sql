--- NEW R HIERARCHY FOR THE PROCESSING METHODS ---

DROP TABLE rhierarchy CASCADE;
CREATE TEMP TABLE IF NOT EXISTS rhierarchy (
    processing_code char(5),
    r_code char(5),
    benchmark_group char(255)
);

INSERT INTO rhierarchy (r_code, processing_code, benchmark_group)
 VALUES ('A', 'B01', 'A Direct hoogwaardig inzetten'), (
         'A',	'B05', 'A Direct hoogwaardig inzetten'), (
         'B',	'B02', 'B Indirect hoogwaardig inzetten'), (
         'B',	'B03', 'B Indirect hoogwaardig inzetten'), (
         'B',	'C04', 'B Indirect hoogwaardig inzetten'), (
         'D',	'E02', 'D Microbiologische verwerking'), (
         'D',	'E03', 'D Microbiologische verwerking'), (
         'D',	'E04', 'D Microbiologische verwerking'), (
         'D',	'E01', 'D Microbiologische verwerking'), (
         'E',	'E05', 'E Grondreiniging'), (
         'E',	'D05', 'E Grondreiniging'), (
         'E',	'F05', 'E Grondreiniging'), (
         'F',	'F03', 'F Verbranding met opbrengst'), (
         'F',	'F04', 'F Verbranding met opbrengst'), (
         'F',	'F06', 'F Verbranding met opbrengst'), (
         'F',	'F07', 'F Verbranding met opbrengst'), (
         'G',	'B04', 'G Verbranden'), (
         'G',	'F01', 'G Verbranden'), (
         'G',	'F02', 'G Verbranden'), (
         'H',	'G02', 'H Storten'), (
         'H',	'G01', 'H Storten')
         , (
         'I', 'A01', 'I Opslag'), (
         'I', 'A02', 'I Opslag'), (
         'C', 'C01', 'C Voorbereiding voor recycling'), (
         'C', 'C02', 'C Voorbereiding voor recycling'), (
         'C', 'C03', 'C Voorbereiding voor recycling'), (
         'C', 'D01', 'C Voorbereiding voor recycling'), (
         'C', 'D02', 'C Voorbereiding voor recycling'), (
         'C', 'D03', 'C Voorbereiding voor recycling'), (
         'C', 'D04', 'C Voorbereiding voor recycling'), (
         'C', 'D06', 'C Voorbereiding voor recycling')
         ;