vault write nytimes/cook-my-list/secret/service-account-keys/google/nyt-news-dev/drone-ci service_account_key=@/Users/gabrielfalcao/Downloads/nyt-news-dev-d7d60e0150dd.json

# vault write $vaultPath $key=@$pathToGSAJson
# vault read vault read nytimes/teams/news-maintainers/secret/monorepo/service-account-keys/google/nyt-news-dev/drone-ci
# vault write nytimes/cook-my-list/secret/foo value=@/Users/gabrielfalcao/Downloads/nyt-news-dev-d7d60e0150dd.json
