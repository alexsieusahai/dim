import json  # keep the configs in json format, really easy to read and parse

def getColorConfig(themeFileName):
    fileStream = open(themeFileName, 'r')
    return json.load(fileStream)

if __name__ == "__main__":
    print(getColorConfig('test.json'))

