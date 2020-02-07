from run import app, init, db


def create_test_data():
    print('Creating test data')

@app.route('/api/delete-all')
def api_delete_all():
    db.drop_all()
    db.create_all()
    return {'status': 'Successfully deleted all database data'}, 200

if __name__ == '__main__':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['TEST_SERVER'] = True

    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print('Clear table %s' % table)
        db.session.execute(table.delete())
    db.session.commit()

    create_test_data()

    init()
