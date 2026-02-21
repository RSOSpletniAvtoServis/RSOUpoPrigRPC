import grpc

import upoprigrpc_pb2
import upoprigrpc_pb2_grpc


def get_usernames():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = upoprigrpc_pb2_grpc.UserServiceStub(channel)

        # -------------------------
        # 1️⃣ Usernames
        # -------------------------
        usernames_response = stub.Usernames(
            upoprigrpc_pb2.GetUsernamesRequest(
                ids=[7, 8, 9],
                uniqueid=123
            )
        )

        print("\nUsernames:")
        for user in usernames_response.usernames:
            print(user.IDUporabnik, user.UporabniskoIme)

# -------------------------
# 2️⃣ Stranka
# -------------------------
def get_stranka():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = upoprigrpc_pb2_grpc.UserServiceStub(channel)
        try:
            stranka_response = stub.Stranka(
                upoprigrpc_pb2.GetStrankaRequest(
                    IDUporabnik=5,
                    uniqueid=123
                )
            )

            print("\nStranka:")
            print(stranka_response)

        except grpc.RpcError as e:
            print("Stranka error:", e.details())  

# -------------------------
# 3️⃣ IzbraneStranke
# -------------------------   

def get_izbranestranke():   
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = upoprigrpc_pb2_grpc.UserServiceStub(channel)    
        izbrane_response = stub.IzbraneStranke(
            upoprigrpc_pb2.GetIzbraneStrankeRequest(
                ids=[1, 2, 3],
                uniqueid=123
            )
        )

        print("\nIzbrane Stranke:")
        for s in izbrane_response.stranke:
            print(s)



def run():
    get_usernames()
    get_stranka()
    get_izbranestranke()






if __name__ == "__main__":
    run()