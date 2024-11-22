-- 清空现有数据
TRUNCATE TABLE model_provider CASCADE;

-- 插入OpenAI提供商
INSERT INTO model_provider (
    id, 
    code, 
    name, 
    model_metadata, 
    description, 
    is_active, 
    created_at
) VALUES (
    'b6d14900-a7c8-4040-b4c9-d58b16b0908d',
    'openai',
    'OpenAI',
    '[
        {
            "field": "base_url",
            "default": "https://api.openai.com/v1",
            "order": 1
        },
        {
            "field": "api_key",
            "default": "",
            "order": 2
        },
        {
            "field": "organization",
            "default": "",
            "order": 3
        }
    ]'::jsonb,
    'OpenAI API provider including GPT-3.5, GPT-4 models',
    true,
    CURRENT_TIMESTAMP
);

-- 插入Anthropic提供商
INSERT INTO model_provider (
    id, 
    code, 
    name, 
    model_metadata, 
    description, 
    is_active, 
    created_at
) VALUES (
    'c7e15011-b8c9-5151-c5d9-e69c27c11a9e',
    'anthropic',
    'Anthropic',
    '[
        {
            "field": "base_url",
            "default": "https://api.anthropic.com",
            "order": 1
        },
        {
            "field": "api_key",
            "default": "",
            "order": 2
        }
    ]'::jsonb,
    'Anthropic API provider including Claude models',
    true,
    CURRENT_TIMESTAMP
);

-- 插入Azure OpenAI提供商
INSERT INTO model_provider (
    id, 
    code, 
    name, 
    model_metadata, 
    description, 
    is_active, 
    created_at
) VALUES (
    'd8f26122-c9d0-6262-d6e0-f70d38d22b0f',
    'azure',
    'Azure OpenAI',
    '[
        {
            "field": "base_url",
            "default": "",
            "order": 1
        },
        {
            "field": "api_key",
            "default": "",
            "order": 2
        },
        {
            "field": "api_version",
            "default": "2024-02-15-preview",
            "order": 3
        },
        {
            "field": "deployment_name",
            "default": "",
            "order": 4
        }
    ]'::jsonb,
    'Azure OpenAI Service provider',
    true,
    CURRENT_TIMESTAMP
);

-- 插入Gemini提供商
INSERT INTO model_provider (
    id, 
    code, 
    name, 
    model_metadata, 
    description, 
    is_active, 
    created_at
) VALUES (
    'e9f37233-d0e1-7373-e7f1-g81e49e33c1g',
    'gemini',
    'Google Gemini',
    '[
        {
            "field": "base_url",
            "default": "https://generativelanguage.googleapis.com/v1",
            "order": 1
        },
        {
            "field": "api_key",
            "default": "",
            "order": 2
        }
    ]'::jsonb,
    'Google Gemini API provider',
    true,
    CURRENT_TIMESTAMP
);

-- 插入Ollama提供商
INSERT INTO model_provider (
    id, 
    code, 
    name, 
    model_metadata, 
    description, 
    is_active, 
    created_at
) VALUES (
    'f0g48344-e1f2-8484-f8g2-h92f50f44d2h',
    'ollama',
    'Ollama',
    '[
        {
            "field": "base_url",
            "default": "http://localhost:11434/api",
            "order": 1
        }
    ]'::jsonb,
    'Ollama local API provider',
    true,
    CURRENT_TIMESTAMP
); 