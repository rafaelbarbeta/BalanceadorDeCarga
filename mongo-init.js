db.createCollection('col_potencias');

db.col_potencias.insert_one(
    {
        timestamp : 0,
        x : 1,
        y : 1,
        resultado : 1,
        microservice: "mongo"
    }
);