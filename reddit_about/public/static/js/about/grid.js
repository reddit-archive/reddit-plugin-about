GridView = Backbone.View.extend({
    initialize: function() {
        this.collection
            .on('add', this.addOne, this)
            .on('reset', this.addAll, this)
            .on('all', _.debounce(this.render), this)

        this.itemViews = {}
        this.addAll()
    },

    createItemView: function(model) {
        return new Backbone.View({model: model})
    },

    addOne: function(model) {
        if (!this.itemViews[model.id]) {
            var view = this.createItemView(model)
            this.itemViews[model.id] = view
        }
    },

    addAll: function() {
        this.collection.each(this.addOne, this)
    },

    render: function() {
        var gridWidth = this.$el.width(),
            gridHeight = 0,
            lastHeight = 0,
            pos = {x:0, y:0},
            sortKey = this.collection.state && this.collection.state.get('sort')

        this.collection.each(function(model) {
            var view = this.itemViews[model.id],
                viewWidth = view.$el.outerWidth(true),
                viewHeight = view.$el.outerHeight(true)

            if (pos.x + viewWidth > gridWidth) {
                pos.x = 0
                pos.y += lastHeight
            }
            lastHeight = viewHeight
            gridHeight = pos.y + viewHeight

            view.$el.css({
                'position': 'absolute',
                'left': pos.x,
                'top': pos.y
            })

            if (sortKey) {
                view.$el.toggleClass('novalue', !model.has(sortKey))
            }

            pos.x += viewWidth
        }, this)

        this.$el
            .css('height', gridHeight)
            .removeClass('loading')
        return this
    }
})
