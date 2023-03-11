import os
import openai
import hashlib
import json
import datetime
from scipy.spatial import distance 

# https://github.com/openai/openai-cookbook/blob/main/examples/Recommendation_using_embeddings.ipynb

# Every string has its embedding looked up and is saved as under its hash
class LongTermMemory():
    def __init__(self, key, model, botname, username):
        openai.api_key = key
        self.model = model or "text-embedding-ada-002";
        self.memory = {}
        
        self.cache_path = os.path.join(".", "memory", f"{botname}_{username}") # TBD prevent bot/username clashes
        if not os.path.exists(self.cache_path):
            os.makedirs(self.cache_path)
       
    def memorize(self, string: str):
        hash = self._hash(string)

        # return if already memorized
        result = self._load(hash)
        if result:
            return result

        # memorize
        embedding = self._get_embedding(string)
        result = {
            'hash': hash, 
            'timestamp': datetime.datetime.now().strftime('%A %d %B %Y %I:%M%p'),
            'string': string, 
            'embedding': embedding
        }
        self._save(hash, result)

        return result

    def recall(self, string, count):
        self._load_cache(self.cache_path) # load new memories (there may be multiple instances running)
        
        thought = self.memorize(string) # get current embedding.  The act of recalling will memorize the current string too.
        
        distances = [
            {
                'string': data['string'], 
                'timestamp': data['timestamp'], 
                'dist': distance.cosine(thought['embedding'], data['embedding'])
            }
            for hash, data in self.memory.items()
        ]
        sorted_by_distance = sorted(distances, key=lambda x: x['dist']) 

        # remove the first item, because its the current item
        top_memories = sorted_by_distance[1:1+count] 

        # print("-----------")
        # print(string)
        # print(json.dumps(top_memories, indent=4))
        # result = [ item['string'] for item in top_memories ]
        result = top_memories

        return result 


    def _get_embedding(self, string):
        response = openai.Embedding.create(model = self.model, input=string)
        result = response["data"][0]["embedding"]
        return result
    
    def _hash(self, string):
        hash = hashlib.md5(string.encode('utf-8'))
        return hash.hexdigest()

    def _save(self, hash, data):
        self.memory[hash] = data
        with open(self._cache_file(hash),'w') as f: 
            json.dump(data,f)
        
    def _load(self, hash):
        # get from memory or initialize to None
        result = self.memory.get(hash, None)
        if result:
            return result

        # get from cache
        fn = self._cache_file(hash)
        if os.path.exists(fn):
            with open(fn, 'r') as f: 
                result = f.read()
                result = json.loads(result)
                self.memory[hash] = result

        # return value or None
        return result


    def _cache_file(self, hash):
        return os.path.join(self.cache_path, hash)

    def _load_cache(self, path):
        for fn in os.listdir(self.cache_path):
            if len(fn) == 32: self._load(fn) # only load hashes

            
        
