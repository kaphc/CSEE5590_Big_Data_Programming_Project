# Spark Sentiment Analysis
spark_sentiment_analysis_log_file_name = '../log_files/spark_sentiment_analysis.log'
twitter_cleaned_data_path = "../data/twitter_cleaned_data.csv"
sentiment_analysis_model_path = "../models/spark_models/sentiment_analysis"
sentiment_tf_idf_model_path = "../models/spark_models/sentiment_tf_idf"

reading_format = 'com.databricks.spark.csv'
read_header = 'true'
infer_schema = 'true'

train_size = 0.98
val_size = 0.01
test_size = 0.01
seed_value = 2000

feature_column_name = "text"
target_column_name = "sentiment"

number_of_features = 2 ** 16
document_frequency = 5
max_iter = 1

# twitter streaming -> tcp
tcp_streaming_log_file_name = "../log_files/tcp_streaming.log"

TCP_IP = "localhost"
port_number = 9009
twitter_streaming_time = 1

# tcp -> spark streaming
spark_streaming_log_file_name = '../log_files/spark_streaming_log_file_name.log'
spark_streaming_time = 2

