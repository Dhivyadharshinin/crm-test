class CodegenRequest:
    qty=product_id=None
    def __init__(self,request):
        self.product=request.GET.get('product')
        self.qty= int(request.GET.get('qty'))