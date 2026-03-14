# Product Requirements Document

## Vision
easypaperless-mcp is a MCP Server for paperless-ngx based on the api wrapper easypaperless. It offers (almost) all functionality in easypaperless and makes it available for ai.

## Target Users
Model Context Protocoll (MCP) Servers are build for ai and allow ai to discover tools, resources and prompts. They are enabled to make good decisions which tool to choose in order to achieve a certain goal. 

## Core Features

* MCP Server offering stdio (for local testing) and streamable-http (for deployment in docker)
* Implement almost all functionality of easypaperless as mcp tools.
* Implement context saving measures, like good defaults and reduced return values
* Guide the ai where necessary. e.g. with additional hints in error cases or with extra artificial return fields (word count of content field).

## Success Metrics
 
* AI is capable to initally setup a new paperless-ngx and/or guide the user during the configuration.
* AI is capable to effiently work on a large number of documents.


## Non Goals
* We don't implement API Calls to paperless-ngx. We fully rely on easypaperless.