from concurrent import futures
import grpc

import upoprigrpc_pb2
import upoprigrpc_pb2_grpc

import mysql.connector
from mysql.connector import pooling
import time

from grpc_health.v1 import health, health_pb2, health_pb2_grpc

for i in range(5):
    try:
        pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="mypool",
            pool_size=5,
            host="34.44.150.229", #127.0.0.1",
            user="zan",
            password=">tnitm&+NqgoA=q6",
            database="RSOUporabnikPrijava",
            autocommit=True
        )
        break
    except Exception as e:
        print("Error: ",e)
        print(f"DB connection failed, retrying... ({i+1}/5)")
        time.sleep(5)
else:
    raise RuntimeError("Could not connect to the database after 5 attempts")


# -------------------------
# Service Implementation
# -------------------------

class UserService(upoprigrpc_pb2_grpc.UserServiceServicer):

    # -------------------------
    # 1️⃣ Usernames
    # -------------------------
    def Usernames(self, request, context):
        response = upoprigrpc_pb2.UsernamesResponse()
        
        # start implementation
        ids_string = "("
        idmiddle = ",".join(str(i) for i in request.ids)
        full_string = "(" + idmiddle + ")"
        print(ids_string)
        print(idmiddle)
        print(full_string)
        
        try:
            with pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "SELECT IDUporabnik, UporabniskoIme FROM Uporabnik WHERE IDUporabnik IN " + full_string
                    cursor.execute(sql)
                    rows = cursor.fetchall()

            for row in rows:
                username = upoprigrpc_pb2.Username(
                    IDUporabnik=int(row[0]),
                    UporabniskoIme=row[1],
                )
                response.usernames.append(username)
            return response
        except Exception as e:
            print("DB error:", e)
            context.abort(grpc.StatusCode.NOT_FOUND, "Error: "+e)
            return response    
        # end implementation
        return response


    # -------------------------
    # 2️⃣ Stranka
    # -------------------------
    def Stranka(self, request, context):
        user_id = request.IDUporabnik
        # implementacija start
        try:
            with pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT IDStranka, Ime, Priimek, Email, Telefon, DavcnaStevilka, IDUporabnik FROM Stranka WHERE IDUporabnik = %s",
                        (user_id,)
                    )

                    row = cursor.fetchone()

                    if row is None:
                        context.abort(grpc.StatusCode.NOT_FOUND, "Error: Stranka not found!")
                        print("Stranka v DB ne obstaja!!!")
                    return upoprigrpc_pb2.StrankaResponse(
                        IDStranka=row[0],
                        Ime=row[1],
                        Priimek=row[2],
                        Email=row[3],
                        Telefon=row[4],
                        DavcnaStevilka=row[5],
                        IDUporabnik=row[6],
                    )
        except Exception as e:
            print("DB error:", e)
            context.abort(grpc.StatusCode.NOT_FOUND, "Error: "+e)
            return {"Stranka": "failed"}
        return {"Stranka": "undefined"}
    # implementacija end



    # -------------------------
    # 3️⃣ IzbraneStranke
    # -------------------------
    def IzbraneStranke(self, request, context):
        response = upoprigrpc_pb2.IzbraneStrankeResponse()
        # implementacija zacetek     
        ids_string = "("
        idmiddle = ",".join(str(i) for i in request.ids)
        full_string = "(" + idmiddle + ")"
        print(ids_string)
        print(idmiddle)
        print(full_string)
        
        try:
            with pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "SELECT IDStranka, Ime, Priimek, Telefon, Email, DavcnaStevilka FROM Stranka WHERE IDStranka IN " + full_string
                    cursor.execute(sql)
                    rows = cursor.fetchall()
                    for row in rows:
                        stranka = upoprigrpc_pb2.Stranka(
                            IDStranka=row[0],
                            Ime=row[1],
                            Priimek=row[2],
                            Telefon=row[3],
                            Email=row[4],
                            DavcnaStevilka=row[5],
                        )
                        response.stranke.append(stranka)
                    return response
        except Exception as e:
            print("DB error:", e)
            context.abort(grpc.StatusCode.NOT_FOUND, "Error: "+e)
            return response
        # implementacija end
        return response


# -------------------------
# Server Setup
# -------------------------

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    upoprigrpc_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    
    # Create health servicer
    health_servicer = health.HealthServicer()

    # Register health service
    health_pb2_grpc.add_HealthServicer_to_server(
        health_servicer, server
    )
    
     # Mark service as NOT_SERVING initially
    health_servicer.set('', health_pb2.HealthCheckResponse.NOT_SERVING)
    
    server.add_insecure_port('[::]:50051')
    server.start()


    # Simulate startup work
    time.sleep(5)

    # Mark as ready
    health_servicer.set('', health_pb2.HealthCheckResponse.SERVING)
    
    print("UserService gRPC server running on port 50051...")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()