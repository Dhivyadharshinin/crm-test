
class TokenHandler:
   def get_token(self,request):
    token_name = request.headers['Authorization']
    # token_split= token_name.split()
    # token = token_split[1]
    header={'Authorization':token_name}
    return header

   def get_headers(self,request):
    token_name = request.headers['Authorization']
    header = {'Authorization': token_name}
    return header