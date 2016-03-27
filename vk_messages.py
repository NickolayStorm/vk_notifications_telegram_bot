import vk


class VkUser:
    def __init__(self, token):
        self.session = get_session(token)
        self.ts, self.pts = get_tses(self.session)

    def get_new_messages(self):

        api = vk.API(self.session)
        new = api.messages.getLongPollHistory(ts=self.ts, pts=self.pts)
        msgs = new['messages']
        self.pts = new["new_pts"]
        count = msgs[0]

        res = []
        if count == 0:
            pass
        else:
            messages = msgs[1:]
            for m in messages:
                uid = m["uid"]
                user = api.users.get(user_ids=uid, fields=[])
                user = user[0]

                data = str(user["first_name"])
                data += " {}".format(user["last_name"])
                data += ": {}".format(m["body"])
                res.append(data)

                print(data)
        return res


def get_session(token):
    return vk.Session(access_token=token)


def get_tses(session):

    api = vk.API(session)

    ts = api.messages.getLongPollServer(need_pts=1)
    pts = ts["pts"]
    ts = ts["ts"]
    return ts, pts
