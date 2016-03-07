from flask.ext.api import App, exceptions
import uuid


app = App(__name__)


def lookup(note_id):
    for note in notes:
        if note['id'] == note_id:
            return note
    raise exceptions.NotFound()


def get_id():
    return '%s' % uuid.uuid4()


notes = [
    {'id': get_id(), 'description': 'Meet someone', 'complete': True},
    {'id': get_id(), 'description': 'Walk somewhere', 'complete': False},
    {'id': get_id(), 'description': 'Do something', 'complete': False},
]


@app.get('/notes/')
def list_notes():
    """
    Returns all existing notes.
    """
    return notes


@app.post('/notes/')
def create_note(description, complete=False):
    """
    Creates a new note.

    * description - A short description of the note.
    * [complete] - True if the task has been completed, False otherwise.
    """
    note = {'id': get_id(), 'description': description, 'complete': complete}
    notes.insert(0, note)
    return note


@app.put('/notes/<note_id>/')
def update_note(note_id, description=None, complete=None):
    """
    Update a note.

    * note_id - The note ID.
    * [description] - A short description of the note.
    * [complete] - True if the task has been completed, False otherwise.
    """
    note = lookup(note_id)
    if description is not None:
        note['description'] = description
    if complete is not None:
        note['complete'] = complete

    return note


@app.delete('/notes/<note_id>/')
def delete_note(note_id):
    """
    Deletes a note.

    * note_id - The note ID.
    """
    note = lookup(note_id)
    notes.remove(note)
    return ''


if __name__ == '__main__':
    app.run(debug=True)
