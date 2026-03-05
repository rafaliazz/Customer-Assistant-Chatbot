SELECT * FROM documents;

-- Create tags based on FAQ, Policy, Troubleshooting, Contact info
UPDATE documents
SET tag = ARRAY[
    CASE WHEN LOWER(prompt) LIKE '%how%' THEN 'how' END,
    CASE WHEN LOWER(prompt) LIKE '%what%' THEN 'what' END,
    CASE WHEN LOWER(prompt) LIKE '%where%' THEN 'where' END,
    CASE WHEN LOWER(prompt) LIKE '%why%' THEN 'why' END,
    CASE WHEN LOWER(prompt) LIKE '%when%' THEN 'when' END,
    CASE WHEN LOWER(prompt) LIKE '%policy%' THEN 'policy' END,
    CASE WHEN LOWER(prompt) LIKE '%rules%' THEN 'rules' END,
    CASE WHEN LOWER(prompt) LIKE '%guideline%' THEN 'guideline' END,
    CASE WHEN LOWER(prompt) LIKE '%terms%' THEN 'terms' END,
    CASE WHEN LOWER(prompt) LIKE '%error%' THEN 'error' END,
    CASE WHEN LOWER(prompt) LIKE '%issue%' THEN 'issue' END,
    CASE WHEN LOWER(prompt) LIKE '%problem%' THEN 'problem' END,
    CASE WHEN LOWER(prompt) LIKE '%fail%' THEN 'failure' END,
    CASE WHEN LOWER(prompt) LIKE '%bug%' THEN 'bug' END,
    CASE WHEN LOWER(prompt) LIKE '%contact%' THEN 'contact' END,
    CASE WHEN LOWER(prompt) LIKE '%email%' THEN 'email' END,
    CASE WHEN LOWER(prompt) LIKE '%phone%' THEN 'phone' END,
    CASE WHEN LOWER(prompt) LIKE '%support%' THEN 'support' END,
    CASE WHEN LOWER(prompt) LIKE '%address%' THEN 'address' END,
    CASE WHEN LOWER(prompt) LIKE '%login%' THEN 'login' END,
    CASE WHEN LOWER(prompt) LIKE '%password%' THEN 'password' END,
    CASE WHEN LOWER(prompt) LIKE '%account%' THEN 'account' END,
    CASE WHEN LOWER(prompt) LIKE '%refund%' THEN 'refund' END,
    CASE WHEN LOWER(prompt) LIKE '%subscription%' THEN 'subscription' END
]::TEXT[];

# Delete nulls from the tag array afterwards
UPDATE documents
SET tag = (
    SELECT ARRAY_AGG(t)
    FROM unnest(tag) AS t
    WHERE t IS NOT NULL
);


