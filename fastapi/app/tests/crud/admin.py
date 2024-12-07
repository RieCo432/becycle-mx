import app.crud as crud
from app.tests.pytestFixtures import *
from sqlalchemy import func, select


def test_find_potential_client_duplicates(clients_with_duplicates):
    assert db.scalar(
        select(func.count(models.DetectedPotentialClientDuplicates.id))
    ) == 0

    crud.find_potential_client_duplicates(db=db)

    detected_duplicates = [_ for _ in db.scalars(
        select(models.DetectedPotentialClientDuplicates)
    )]

    assert len(detected_duplicates) == 4

    expected_duplicate_client_ids = [set([clients_with_duplicates[i].id, clients_with_duplicates[j].id]) for (i, j) in [[0, 2], [3, 1], [4, 1], [4, 3]]]
    expected_similarity_scores = [5, 2, 5, 2]

    for detected_duplicate in detected_duplicates:
        assert detected_duplicate.similarityScore in expected_similarity_scores
        expected_similarity_scores.remove(detected_duplicate.similarityScore)

        set_of_client_ids = set([detected_duplicate.client1Id, detected_duplicate.client2Id])
        assert set_of_client_ids in expected_duplicate_client_ids
        expected_duplicate_client_ids.remove(set_of_client_ids)

    db.query(models.DetectedPotentialClientDuplicates).delete()
    db.commit()


def test_find_potential_client_duplicates_all_found(clients_with_duplicates, detected_potential_client_duplicates):
    assert db.scalar(
        select(func.count(models.DetectedPotentialClientDuplicates.id))
    ) == 4

    crud.find_potential_client_duplicates(db=db)

    detected_duplicates = [_ for _ in db.scalars(
        select(models.DetectedPotentialClientDuplicates)
    )]

    assert len(detected_duplicates) == 4


def test_find_potential_bike_duplicates(bikes_with_duplicates):
    assert db.scalar(
        select(func.count(models.DetectedPotentialBikeDuplicates.id))
    ) == 0

    crud.find_potential_bike_duplicates(db=db)

    detected_duplicates = [_ for _ in db.scalars(
        select(models.DetectedPotentialBikeDuplicates)
    )]

    assert len(detected_duplicates) == 5

    expected_duplicate_bike_ids = [set([bikes_with_duplicates[i].id, bikes_with_duplicates[j].id]) for (i, j) in [[0, 2], [1, 6], [5, 4], [4, 10], [10, 5]]]
    expected_similarity_scores = [5, 4, 7, 5, 8]

    for detected_duplicate in detected_duplicates:
        assert detected_duplicate.similarityScore in expected_similarity_scores
        expected_similarity_scores.remove(detected_duplicate.similarityScore)

        set_of_bike_ids = set([detected_duplicate.bike1Id, detected_duplicate.bike2Id])
        assert set_of_bike_ids in expected_duplicate_bike_ids
        expected_duplicate_bike_ids.remove(set_of_bike_ids)

    db.query(models.DetectedPotentialBikeDuplicates).delete()
    db.commit()


def test_find_potential_bike_duplicates_all_found(bikes_with_duplicates, detected_potential_bike_duplicates):
    assert db.scalar(
        select(func.count(models.DetectedPotentialBikeDuplicates.id))
    ) == 5

    crud.find_potential_bike_duplicates(db=db)

    detected_duplicates = [_ for _ in db.scalars(
        select(models.DetectedPotentialBikeDuplicates)
    )]

    assert len(detected_duplicates) == 5
