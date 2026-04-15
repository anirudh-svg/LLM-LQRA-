LQRA is a rust based graphing method, used to handle LLM as a database. 
Query neural network weights like a graph database. Lazarus Query Language.
A vindex is a directory containing a model's weights reorganised for queryability. Gate vectors become a KNN index. Embeddings become token lookups. Down projections become edge labels. The model IS the database.

Larql-lql
LQL parser and executor. 20+ statement types across 5 categories:

Lifecycle: EXTRACT, COMPILE, DIFF, USE
Browse: WALK, DESCRIBE, SELECT, EXPLAIN WALK
Inference: INFER, EXPLAIN INFER
Mutation: INSERT, DELETE, UPDATE, MERGE
Patches: BEGIN PATCH, SAVE PATCH, APPLY PATCH, SHOW PATCHES, REMOVE PATCH
Introspection: SHOW RELATIONS/LAYERS/FEATURES/MODELS/PATCHES, STATS

The features of LQRA can theoritically be used for making changes/updates to knowledge in the LLM without doing re training. 

