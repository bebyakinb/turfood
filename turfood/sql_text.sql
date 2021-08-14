CREATE TABLE Products (
	Id integer,
	Name string,
	DietType_id integer,
	Fats float,
	Carbs float,
	Proteins float
);

CREATE TABLE Recipes_products_sets (
	Id integer,
	Recipe_Id integer,
	Product_Id integer,
	Amount decimal,
	Recipe_type_id binary
);









