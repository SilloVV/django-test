from django.db import models


class Driver(models.Model):
    user = models.OneToOneField(
        "users.User", on_delete=models.CASCADE, related_name="driver"
    )

    def __str__(self):
        return f"Driver: {self.user.username} (id: {self.pk})"


class Bus(models.Model):
    licence_plate = models.CharField("Name of the bus", max_length=10)

    class Meta:
        verbose_name_plural = "Buses"

    def __str__(self):
        return f"Bus: {self.licence_plate} (id: {self.pk})"


class BusShift(models.Model):
    """Classe définissant un trajet en Bus
    éléments:
    - Un Bus (Unique)
    - Un Conducteur (Unique)
    - Une liste d'arrets > 2 (à définir)
    """

    bus = models.ForeignKey(
        Bus, on_delete=models.CASCADE, related_name="shifts"
    )  # ForeignKey ne peut etre null et est unique
    driver = models.ForeignKey(
        Driver, on_delete=models.CASCADE, related_name="shifts"
    )  # ForeignKey ne peut etre null et est unique

    class Meta:
        verbose_name = "Bus Shift"
        verbose_name_plural = "Bus Shifts"

    def __str__(self):
        return f"BusShift Numéro {self.pk} - Bus:{self.bus} / Conducteur: {self.driver}"

    @property
    # départ : stops calculé depuis BusStops
    def departure_time(self):
        first = self.stops.order_by("passage_time").first()
        return first.passage_time if first else None

    @property
    # temps d'arrivé : stops calculé depuis BusStops
    def arrival_time(self):
        last = self.stops.order_by("passage_time").last()
        return last.passage_time if last else None

    @property
    # Durée de trajet
    def duration(self):
        if self.departure_time and self.arrival_time:
            return self.arrival_time - self.departure_time
        return None


class BusStop(models.Model):
    """Classe définissant un arret de Bus :
    éléments :
    - Trajet : Non Null et Unique
    - Endroit : Unique et non NULL
    - Temps de passage : unique et non nul et NULL
    """

    bus_shift = models.ForeignKey(
        BusShift, on_delete=models.CASCADE, related_name="stops"
    )
    place = models.ForeignKey(
        "geography.Place", on_delete=models.CASCADE, related_name="bus_stops"
    )
    passage_time = models.DateTimeField("Temps de passage")  # manque une validation ici

    class Meta:
        ordering = ["passage_time"]
        verbose_name = "Bus Stop"
        verbose_name_plural = "Bus Stops"

    def __str__(self):
        return f"Stop au {self.place} à {self.passage_time}"

    # Si on veut s'assurer que la date est bien dans le futur et éviter des passages dans le passé
    # def clean(self):
    #  if self.passage_time and self.passage_time < timezone.now():
    #      raise ValidationError("La date de passage doit être dans le futur.")
