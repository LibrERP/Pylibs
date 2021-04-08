from pathlib import Path
import ast
import argparse

import graphviz


class DepGraphBuilder:

    def __init__(
            self,
            root_dir_path: Path,
            out_dir_path: Path,
            out_file_name: str,
            show_graph: bool = False
    ):
        self._root_path = root_dir_path
        self._out_dir_path = out_dir_path
        self._out_file_name = out_file_name
        self._show_graph = show_graph
    # end __init__

    def build_graph(self):

        dg = graphviz.Digraph(
            name='Odoo dependencies',
            directory=self._out_dir_path,
            filename=self._out_file_name,
            graph_attr={
                'overlap': 'false',
                'splines': 'true',
            },
            node_attr={
                'shape': 'box',
            },
        )

        manifests_by_module = {
            manifest.parent.name: self.read_manifest(manifest)
            for manifest in self._root_path.glob('**/__manifest__.py')
        }

        for mod_name, mod_manifest in manifests_by_module.items():

            deps_list = mod_manifest.get('depends', list())
            deps_list_filtered = list(filter(
                lambda d: d in manifests_by_module,
                deps_list
            ))

            if deps_list_filtered:
                for dep_name in deps_list_filtered:
                    dg.edge(mod_name, dep_name)
                # end for

            else:
                dg.node(mod_name)

            # end if

        # end for

        dg.render(view=self._show_graph)
    # end build_graph

    @staticmethod
    def read_manifest(filepath: Path):
        py_dict = ast.literal_eval(filepath.read_text())
        return py_dict
    # end read_manifest

# end DepGraphBuilder


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-i',
        '--indir',
        type=Path,
        default=Path('.'),
        help='Base directory where to search for modules. '
             'Default: current directory'
    )

    parser.add_argument(
        '-o',
        '--outdir',
        type=Path,
        default=Path('.'),
        help='Output directory path: '
             'this directory will store the graphviz'
             'file (.gv) and the PDF file. '
             'Default: current directory'
    )

    parser.add_argument(
        '-f',
        '--filename',
        type=str,
        default='modules_deps',
        help='Output file name WITOUT extention. '
             'Two files are created: <filename>.gv and <filename>.pdf file'
    )

    parser.add_argument(
        '-s',
        '--show',
        action='store_true',
        default=False,
        help='Open the generated graph in a window after rendering is complete'
    )

    args = parser.parse_args()

    dgb = DepGraphBuilder(
        root_dir_path=args.indir,
        out_dir_path=args.outdir,
        out_file_name=args.filename,
        show_graph=args.show
    )

    dgb.build_graph()

# end if
