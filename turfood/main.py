from db_filling import TurFoodDB


def main():
    db = TurFoodDB()
    print(db.table_names)
    db.get_google_spreadsheet_data()


if __name__ == '__main__':
    main()
