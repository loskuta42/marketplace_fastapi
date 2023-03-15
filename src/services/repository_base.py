from abc import ABC, abstractmethod


class Repository(ABC):

    @abstractmethod
    def get_by_id(self, *args, **kwargs):
        ...

    @abstractmethod
    def get_multi(self, *args, **kwargs):
        ...

    @abstractmethod
    def create(self, *args, **kwargs):
        ...

    @abstractmethod
    def patch(self, *args, **kwargs):
        ...

    @abstractmethod
    def delete(self, *args, **kwargs):
        ...
