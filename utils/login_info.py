from face.serializers import UserDetailSerializer


def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt认证成功返回数据
    :token  返回的jwt
    :user   当前登录的用户信息[对象]
    :request 当前本次客户端提交过来的数据
    """
    # print('token:'+token)
    # print('user:',user)
    # return {
    #     'token': token,
    #     'id': user.id,
    #     'username': user.username,
    #     'number': str(user.number),
    #     'sex': user.sex,
    #     'face': str(user.face)
    # }
    return {
        'token': token,
        'user': UserDetailSerializer(user, context={'request': request}).data
    }
