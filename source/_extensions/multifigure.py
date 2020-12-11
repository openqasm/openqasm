# -*- coding: utf-8 -*-
import itertools

from docutils.parsers.rst import Directive, directives
from docutils import nodes


DEFAULT_ROW_ITEM_COUNT = 4
MULTIFIGURE_HTML_CONTENT_TAG = 'div'
MULTIFIGURE_HTML_ITEM_TAG = 'div'
MULTIFIGURE_HTML_CAPTION_TAG = 'span'


class multifigure_content(nodes.General, nodes.Element):
    """Node for grouping and laying out all the images in a multi-figure."""


class multifigure_item(nodes.General, nodes.Element):
    """Node representing one of the images inside a multi-figure."""


def label_list(argument):
    return [
        label
        for label in (label.strip() for label in argument.split(' '))
        if label
    ]


class MultiFigure(Directive):
    """
    Directive for creating multi-image figures, called multifigures.

    Options:
    --------
    ``rowitems``: maximum number of items per row. Default is 4.
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    option_spec = {
        'rowitems': directives.positive_int,
        'labels': label_list
    }

    def run(self):
        env = self.state.document.settings.env

        node = nodes.Element()
        node.document = self.state.document
        self.state.nested_parse(self.content, self.content_offset, node)

        images = []
        caption_and_legend = []
        for child in node:
            if isinstance(child, (nodes.target, nodes.image, nodes.figure)):
                images.append(child)
            else:
                caption_and_legend.append(child)

        items = []
        row_item_count = min(
            len(images), self.options.get('rowitems', DEFAULT_ROW_ITEM_COUNT))
        labels = self.options.get('labels', [])
        for img, label in itertools.zip_longest(images, labels):
            item_node = multifigure_item('', img)
            item_node['item-width'] = 100 // row_item_count
            if label is not None:
                item_node['label'] = label
            items.append(item_node)

        caption, legend = caption_and_legend[0], caption_and_legend[1:]

        resultnode = nodes.figure('', multifigure_content('', *items))
        resultnode['labels'] = labels
        resultnode.append(nodes.caption(caption.rawsource, '', *caption))
        if legend:
            resultnode.append(nodes.legend('', *legend))

        return [resultnode]


def visit_multifigure_content_html(self, node):
    alignment = 'baseline' if node.parent.get('labels') else 'center'
    self.body.append(self.starttag(
        node,
        MULTIFIGURE_HTML_CONTENT_TAG,
        CLASS='figure-content',
        style=' '.join((
            'display: flex;',
            'gap: 2rem 0;',
            'flex-direction: row;',
            'justify-content: center;',
            'align-items: %s;' % alignment,
            'flex-wrap: wrap;'))
    ))


def depart_multifigure_content_html(self, node):
    self.body.append('</%s>\n' % MULTIFIGURE_HTML_CONTENT_TAG)


def visit_multifigure_item_html(self, node):
    self.body.append(self.starttag(
        node,
        MULTIFIGURE_HTML_ITEM_TAG,
        CLASS='figure-item',
        style=' '.join((
            'max-height: 10rem;',
            'width: %i%%;' % node.get('item-width'),
            'display: flex;',
            'flex-direction: column;'))
    ))


def depart_multifigure_item_html(self, node):
    if node.get('label'):
        self.body.append(self.starttag(
            node,
            'p',
            CLASS='caption'
        ))
        self.body.append(self.starttag(
            node,
            MULTIFIGURE_HTML_CAPTION_TAG,
            CLASS='caption-number'
        ))
        self.body.append(node.get('label'))
        self.body.append('</p>\n')
        self.body.append('</%s>\n' % MULTIFIGURE_HTML_CAPTION_TAG)
    self.body.append('</%s>\n' % MULTIFIGURE_HTML_ITEM_TAG)


def setup(app):
    app.add_node(
        multifigure_content,
        html=(visit_multifigure_content_html, depart_multifigure_content_html))
    app.add_node(
        multifigure_item,
        html=(visit_multifigure_item_html, depart_multifigure_item_html))
    app.add_directive('multifigure', MultiFigure)
    return {'parallel_read_safe': True}
