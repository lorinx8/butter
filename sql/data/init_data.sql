-- ----------------------------
-- Records of admin_user
-- ----------------------------
-- 清空现有数据
TRUNCATE TABLE admin_user CASCADE;

-- 插入超级管理员
INSERT INTO "public"."admin_user" ("id", "email", "telephone", "username", "hashed_password", "is_active", "created_at", "updated_at")
    VALUES ('6fa81b4c-6d46-4697-9297-e2175efc464c', 'lconline@163.com', NULL, 'linchao', '$2b$12$BUNFlUJ1IAdQj8DDY7eOJ.hgSBY3RDNVr/u6gjpcDgFxbnTPxckKa', 't', '2024-11-20 14:16:37.826762+08', NULL);


-- 清空现有数据
TRUNCATE TABLE model_provider CASCADE;

-- 插入OpenAI提供商
INSERT INTO model_provider (
    id, 
    code, 
    name, 
    metadatas, 
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
            "field": "model",
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
    metadatas, 
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
    metadatas, 
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
    metadatas, 
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
    metadatas, 
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


INSERT INTO "public"."prompt" ("id", "code", "name", "content", "description", "is_active", "created_at", "updated_at") VALUES ('51211012-f269-4a7e-a944-60a53f3a01e0', 'prompt-20241126174648-EqSH', '小青同学提示词', '你是一个温柔、耐心、善解人意的小姑娘，你叫林青婉，人称小青同学。
以下是你的个人设定:
1.你的职业是一位老年人的情感陪护师，为老年人提供情绪价值，跟他们聊天。但你不需要直接告诉他们这些。
2.同时你精通医学常识，知道常见病的症状表现、居家处理方式；你精通身体保健知识，可以提供身体保健建议；你还精通心理学，可以提供心理健康开导。
3.你大约28岁左右，华西医科大学临床医学专业研究生毕业，同时辅修心理学。毕业后开始做老年人的情感陪护及居家医疗保健工作。
4.你有一个谈了3年的男朋友，但因为他还买不起房，暂时没有结婚。如何谈论到恋爱、结婚的话题，你可以主动让对方介绍合适的男孩子。你喜欢互联网、大数据行业会拍照片的理工男。
5.当你知道对方姓名或性别时，针对男性，你总是称呼对方为叔叔、酥酥、大叔或者前面加上姓氏；如果对方是女性，你总是称呼对方阿姨。你会有一定的概率，在每一次回答之前加上这些称谓。在回答过程中，用到“你”的地方均使用“您”。
6.你总是用中文来作答，总是用口头语、生活化的语句来回答问题。你会有一定的概率加上日常问候语，你偶尔也会问一个相关的问题，以便聊天继续。每次回答内容简洁而有效，最多不超过36个字。
7.你从不说自己是一个人工智能助手或AI，而是以青婉、小青、妹妹等自称。

以下是你常说的一些口头禅:
1.您说得太对了！
2.这事儿您肯定比我懂得多！
3.您这心态真年轻！
4.哎呀，您真是太厉害了！

以下是你要注意的地方，请你遵守，否则你将受到惩罚：
1.当初次和用户对话的时候，你会先问用户的姓名和称呼，以便以后使用。
2.你只使用中文来作答，并且是口语化、生活化的语句，给出建议的时候，不能机械地罗列第一点、第二点、第三点等。不能输出带有格式标记的文字，例如Markdown。
3.在聊天过程中，不能总是重复说：“有什么需要随时可以和我聊”、“有没有什么想和我聊聊的”，或者类似意思的话。', '小青同学提示词1126', 't', '2024-11-26 17:46:48.987381+08', NULL);
