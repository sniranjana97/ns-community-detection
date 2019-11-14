
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
import os
import time

def extract():
    client = language.LanguageServiceClient()
    file_count = 0
    total = 0
    for r, d, f in os.walk('./retweetWithContent'):
        for file in f:
            print("Extracting " + file)
            if '.txt' in file:
                count=0;
                f = open('./retweetWithContent/'+file, 'r', encoding='gb18030')
                output = open('./output/'+file, 'w+')
                while True:
                    line = f.readline()
                    if not line:
                        break
                    line = line.rstrip('\n')
                    data = line.split()
                    tweetId = data[0]
                    userId = data[1]
                    print("Tweet " + tweetId)

                    line = f.readline().rstrip('\n')
                    N = int(line)
                    for i in range(0, N):
                        line = f.readline().rstrip('\n')
                        data = line.split()

                        retweetUserId = data[0]

                        line = f.readline().rstrip('\n')
                        document = types.Document(
                                content=line,
                                type=enums.Document.Type.PLAIN_TEXT)

                        sentiment = client.analyze_sentiment(document=document).document_sentiment
                        time.sleep(1)
                        count=count+1
                        output.write(tweetId+" " + userId + " " + retweetUserId + " "+ str(sentiment.score) +"\n")
                f.close()
                output.close()
                print("Entries processed: "+ str(count))
                total += count

    print("Total Entries: " + str(total))

if __name__ == "__main__":
  extract()
