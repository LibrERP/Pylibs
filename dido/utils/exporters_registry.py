from collections import defaultdict


class ExportersRegistry:
    """
        Register of available exporters to be populated using the
        "register_exporter" class method.
    """
    _exporters_by_backend = defaultdict(dict)

    @classmethod
    def register_exporter(cls, collection_name: str, binding_class):
        """Method to populate the importers register.

        This method is to be used with the backend definition for the connector
        to automatically populate the available importers register"""
        model = binding_class._name
        friendly_name = binding_class._description

        cls._exporters_by_backend[collection_name][model] = friendly_name
    # end register_importer

    @classmethod
    def exporters(cls, backend_name: str):
        selection = sorted(
            cls._exporters_by_backend[backend_name].items(),
            key=lambda x: x[1]
        )
        return selection
    # end importers

    @classmethod
    def is_registered(cls, collection_name: str, binding_class):
        model = binding_class._name
        collection = cls._exporters_by_backend.get(collection_name, {})
        return model in collection
    # end is_registered

# end ExportersRegistry
