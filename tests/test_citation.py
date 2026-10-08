from roster.citation import Citation

def test_citation_identifies_source_chunk(): assert Citation("readme",2,"README").chunk_index==2
