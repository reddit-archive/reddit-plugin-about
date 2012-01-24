SlideshowView = Backbone.View.extend({
    events: {
        'click button.prev': 'prev',
        'click button.next': 'next',
        'mouseover': 'pause',
        'mouseout': 'play'
    },

    initialize: function() {
        this.collection.bind('reset', this.render, this)
        this.index = 0
        this.$('.image').empty()
    },

    _delta: function(delta) {
        return (this.collection.length + this.index + delta) % this.collection.length
    },

    _image: function(cls, index) {
        var image = this.collection.at(index)
        var $img = this.$('.image .id-'+index)
        if (!$img.length) {
            $img = $('<img>').appendTo(this.$('.image'))
        }
        $img.attr({
            'src': image.get('src'),
            'alt': image.get('title'),
            'class': cls + ' id-'+index
        })
    },

    render: function() {
        this._image('prev', this._delta(-1))
        this._image('current', this.index)
        this._image('next', this._delta(1))
        this.$('.current-index').text(this.index + 1)
        this.$('.total').text(this.collection.length)
        return this
    },

    prev: function() {
        this.index = this._delta(-1)
        this.render()
    },

    next: function() {
        this.index = this._delta(1)
        this.render()
    },

    play: function() {
        if (!this._interval) {
            this._interval = setInterval(_.bind(this.next, this), this.interval)
        }
        this.render()
    },

    pause: function() {
        if (this._interval) {
            clearInterval(this._interval)
            this._interval = null
        }
    }
})
