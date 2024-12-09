class ElementsHtml:
    BASIC = """
    <!DOCTYPE html>
    <html>
      <head>
        <title>API Documentation</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <script src="https://unpkg.com/@stoplight/elements/web-components.min.js"></script>
        <link rel="stylesheet" href="https://unpkg.com/@stoplight/elements/styles.min.css">
      </head>
      <body>
        <elements-api
          apiDescriptionUrl="/openapi.json"
          router="hash"
          layout="sidebar"
        />
      </body>
    </html>
    """

    '''
        apiDescriptionUrl: OpenAPI 文档的URL
        router: 路由模式 ("hash" 或 "memory")
        layout: 布局模式 ("sidebar" 或 "stacked")
        hideTryIt: 是否隐藏试用功能
        hideExport: 是否隐藏导出功能
        hideInternal: 是否隐藏内部API
        logo: 自定义logo URL
    '''
    ADVANCED = """
    <!DOCTYPE html>
    <html>
      <head>
        <title>API Documentation</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <script src="https://unpkg.com/@stoplight/elements/web-components.min.js"></script>
        <link rel="stylesheet" href="https://unpkg.com/@stoplight/elements/styles.min.css">
        <style>
          body {
            margin: 0;
            padding: 0;
          }
          elements-api {
            display: block;
            height: 100vh;
          }
        </style>
      </head>
      <body>
        <elements-api
          apiDescriptionUrl="/openapi.json"
          router="hash"
          layout="sidebar"
          hideTryIt="false"
          hideExport="false"
          hideInternal="true"
        />
      </body>
    </html>
    """