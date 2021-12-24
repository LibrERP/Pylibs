from collections import defaultdict


class ImportersRegistry:

    # Register of available importers to be populated using the
    # "register_importer" class method as a decorator of the
    # backend class of the connector.
    _importers_by_backend = defaultdict(dict)

    @classmethod
    def register_importer(cls, collection_name, binding_class):
        """Method to populate the importers register.

        This method is to be used with the backend definition for the connector
        to automatically populate the available importers register"""
        model = binding_class._name
        friendly_name = binding_class._description

        cls._importers_by_backend[collection_name][model] = friendly_name
    # end register_importer

    @classmethod
    def importers(cls, collection_name):
        selection = sorted(
            cls._importers_by_backend[collection_name].items(),
            key=lambda x: x[1]
        )
        return selection
    # end importers

# end ImportersRegistry
