from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
import socket
import json
import time
import Logger
import Constants
import credentials.twitter_credentials as tc
import pyspark as ps
from pyspark.sql import SQLContext
from pyspark.ml import PipelineModel
from pyspark.ml.classification import LogisticRegressionModel


def set_up_tcp_connection(log):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket object
    host = Constants.TCP_IP  # Get local machine name
    port = Constants.port_number  # Reserve a port for your service.
    s.bind((host, port))  # Bind to the port
    log.info("Listening on port: %s" % str(port))
    return s


def set_twitter_authentication(log):
    log.info("Twitter Authentication has been setup successfully")
    consumer_key = tc.consumerKey
    consumer_secret = tc.consumerSecret
    access_token = tc.accessToken
    access_secret = tc.accessTokenSecret
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    return auth


def create_spark_context(log):
    try:
        conf = ps.SparkConf().setAll([('spark.executor.memory', '16g'), ('spark.driver.memory', '16g')])
        sc = ps.SparkContext(conf=conf)
        sql_c = SQLContext(sc)
        log.info("Created a Spark Context")
        return sql_c, sc
    except ValueError as e:
        log.error(e)


class TweetsListener(StreamListener):

    def __init__(self, csocket):
        super().__init__()
        self.client_socket = csocket

    def on_data(self, data):
        try:
            s = self.client_socket
            s.listen(5)  # Now wait for client connection.
            c, addr = s.accept()  # Establish connection with client.
            print("Received request from: " + str(addr))
            msg = json.loads(data)

            tweet_time = msg['created_at']
            text = msg['text'].replace('\n', '')
            hashtags = " "
            if msg['entities'] is not None:
                if msg['entities']['hashtags'] is not None:
                    for hashtag in msg['entities']['hashtags']:
                        hashtags = hashtags + " " + hashtag['text']

            model = PipelineModel.load(Constants.sentiment_tf_idf_model_path)
            v = sql_context.createDataFrame([
                ("a", msg['text'].replace('\n', '')),
            ], ["_c0", "text"])
            v = model.transform(v)
            model2 = LogisticRegressionModel.load(Constants.sentiment_analysis_model_path)
            v = model2.transform(v)
            v_list = v.select('prediction').collect()
            sentiment = str(v_list[0].prediction)

            s_data = tweet_time + ' ~@ ' + text + ' ~@ ' + sentiment + ' ~@ ' + str(hashtags)

            print(s_data.encode('utf-8'))
            c.send(s_data.encode('utf-8'))
            c.close()
        except BaseException as e:
            print("Error on_data: %s" % str(e))
        return True

    def on_error(self, status):
        print(status)
        return True


if __name__ == "__main__":
    start_time = time.time()
    log_file = Logger.LoggerFile()
    logger = log_file.set_logger_file('Twitter Streaming to TCP',
                                      Constants.spark_streaming_log_file_name)

    sql_context, spark_context = create_spark_context(logger)

    socket_object = set_up_tcp_connection(logger)
    twitter_auth = set_twitter_authentication(logger)

    twitter_stream = Stream(twitter_auth, TweetsListener(socket_object))
    twitter_stream.filter(track="Apple")
