from datetime import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from padam_django.apps.fleet.factories import BusFactory, DriverFactory
from padam_django.apps.fleet.models import BusShift, BusStop
from padam_django.apps.geography.factories import PlaceFactory


def make_aware(hour):
    return timezone.make_aware(
        datetime(2024, 1, 1, hour, 0)
    )  # make_aware permet d allouer une timezone


class BusOverlapTest(TestCase):
    def setUp(self):
        self.bus1 = BusFactory()
        self.bus2 = BusFactory()
        self.driver1 = DriverFactory()
        self.driver2 = DriverFactory()
        self.place1 = PlaceFactory()
        self.place2 = PlaceFactory()

    def _create_shift(self, bus, driver, start_hour, end_hour):
        shift = BusShift.objects.create(bus=bus, driver=driver)
        BusStop.objects.create(
            bus_shift=shift, place=self.place1, passage_time=make_aware(start_hour)
        )
        BusStop.objects.create(
            bus_shift=shift, place=self.place2, passage_time=make_aware(end_hour)
        )
        return shift

    # --- Chevauchement bus ---
    # -> Doit retourner une erreur : pas implémenté
    def test_bus_overlap_b_starts_during_a(self):
        """Situation : Même bus : B commence pendant A
        Résultat : Si ValidationError -> le test passe OK"""
        self._create_shift(self.bus1, self.driver1, 9, 11)
        shift2 = self._create_shift(self.bus1, self.driver2, 10, 12)
        with self.assertRaises(ValidationError):
            shift2.full_clean()

    def test_bus_overlap_b_inside_a(self):
        """Situation : Même bus : B entièrement dans A
        Résultat : Si ValidationError -> le test passe OK"""
        self._create_shift(self.bus1, self.driver1, 9, 13)
        shift2 = self._create_shift(self.bus1, self.driver2, 10, 12)
        with self.assertRaises(ValidationError):
            shift2.full_clean()

    # --- Pas de chevauchement bus ---

    def test_bus_no_overlap_sequential(self):
        """Situation: Même bus : B commence après la fin de A
        Résultat: Le test passe si pas d'erreur."""
        self._create_shift(self.bus1, self.driver1, 9, 11)
        shift2 = self._create_shift(self.bus1, self.driver2, 12, 14)
        shift2.full_clean()

    def test_bus_no_overlap_different_bus(self):
        """Situation: Bus différents, même créneau
        Résultat: Le test passe si pas d'erreur."""
        self._create_shift(self.bus1, self.driver1, 9, 11)
        shift2 = self._create_shift(self.bus2, self.driver2, 9, 11)
        shift2.full_clean()

    # --- Chevauchement driver ---
    # -> Doit retourner une erreur : pas implémenté
    def test_driver_overlap(self):
        """Situation: Même driver : trajets qui se chevauchent
        Résultat: Le test passe si une ValidationError est retournée"""
        self._create_shift(self.bus1, self.driver1, 9, 11)
        shift2 = self._create_shift(self.bus2, self.driver1, 10, 12)
        with self.assertRaises(ValidationError):
            shift2.full_clean()

    # --- Pas de chevauchement driver ---

    def test_driver_no_overlap_sequential(self):
        """Situation: Même driver : trajets séquentiels
        Résultat: Le test passe si pas d'erreur."""
        self._create_shift(self.bus1, self.driver1, 9, 11)
        shift2 = self._create_shift(self.bus2, self.driver1, 12, 14)
        shift2.full_clean()
