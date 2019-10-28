import tweepy
import csv
import json

from google.cloud import language_v1
from google.cloud.language_v1 import enums


def get_twitter_credentials(key):
    with open('credentials/twitter_credential.json') as json_file:
        data = json.load(json_file)
        return data[key]


def find_key_in_dictionary(entities, key):
    if key in entities:
        return str(entities[key]).encode("utf-8", errors='ignore')
    return ""


def sample_classify_text(client, text_content):
    type_ = enums.Document.Type.PLAIN_TEXT
    language = "en"
    document = {"content": text_content, "type": type_, "language": language}
    response = client.classify_text(document)
    for category in response.categories:
        if str(category.name).startswith('/Business') or str(category.name).startswith('/Finance') \
                or str(category.name).startswith('/Science') or str(category.name).startswith('/News'):
            return True
    return False


if __name__ == '__main__':

    # twitter authentication
    auth = tweepy.OAuthHandler(get_twitter_credentials('consumerKey'), get_twitter_credentials('consumerSecret'))
    auth.set_access_token(get_twitter_credentials('accessToken'), get_twitter_credentials('accessTokenSecret'))
    api = tweepy.API(auth, wait_on_rate_limit=True)

    client = language_v1.LanguageServiceClient()

    with open("company_list.txt") as f:
        companies = f.readlines()
    companies = [x.strip() for x in companies]

    for company in companies:
        csvCursor = open('data/twitter_data/' + company + '.csv', 'a', newline='')
        csvWriter = csv.writer(csvCursor)

        count = 0
        for tweet in tweepy.Cursor(api.search, q="Amazon", count=10000000, lang="en", since="2000-01-01",
                                   include_entities=True).items():
            if len(str(tweet.text).encode("utf-8", errors='ignore').split()) > 20:
                try:
                    if sample_classify_text(client, str(tweet.text).encode("utf-8", errors='ignore')):
                        print(count)
                        count = count + 1
                        csvWriter.writerow([str(tweet.created_at).encode("utf-8", errors='ignore').decode(),
                                            str(tweet.id_str).encode("utf-8", errors='ignore'),
                                            str(tweet.text).encode("utf-8", errors='ignore'),
                                            str(tweet.user.id).encode("utf-8", errors='ignore'),
                                            str(tweet.user.name).encode("utf-8", errors='ignore'),
                                            str(tweet.user.screen_name).encode("utf-8", errors='ignore'),
                                            str(tweet.user.location).encode("utf-8", errors='ignore'),
                                            str(tweet.user.url).encode("utf-8", errors='ignore'),
                                            str(tweet.user.description).encode("utf-8", errors='ignore'),
                                            str(tweet.place).encode("utf-8", errors='ignore'),
                                            find_key_in_dictionary(tweet.entities, "hashtags"),
                                            find_key_in_dictionary(tweet.entities, "urls"),
                                            find_key_in_dictionary(tweet.entities, "user_mentions")])
                except:
                    print("exception")

        csvCursor.close()
