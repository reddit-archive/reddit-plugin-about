TimelineEvent = Backbone.Model.extend({})
TimelineEventCollection = Backbone.Collection.extend({
    model: TimelineEvent,
    comparator: function(model) {
        return Number(model.get("date"))
    }
})


TimelineEventView = Backbone.View.extend({
    initialize: function() {
        // Scrape the model data from the DOM.
        this.model = new TimelineEvent({
            'date': Date.parse(this.$('time').attr('datetime')),
            'class': this.$el.attr('class'),
            'title': this.$('.title').text()
        })
    },

    render: function() {
        this.$('.event-content').wrap('<div class="event-marker">')
        return this
    },

    positionDot: function(percentage) {
        this.$el.css('left', percentage)
    },

    positionLabel: function(yDelta, leftOffset, z, side) {
        this.$el.css('z-index', z)

        this.$('.event-marker')
            .css({
                'height': '+='+yDelta,
                // Scale the marker to the width of the content, if space is
                // available to provide a large hover target.
                'width': this.$('.event-content').width() + leftOffset
            })
            .addClass(side)

        this.$('.event-content')
            .show()
            .css('left', leftOffset)
            .toggleClass('offset', leftOffset != 0)
    },

    labelWidth: function() {
        return this.$('.event-content').outerWidth(true)
    }
})

TimelineView = Backbone.View.extend({
    // Spacing between rows on the timeline.
    rowHeight: 30,

    events: {
        'mouseover .event': 'focusEvent',
        'mouseout .event': 'unfocusEvent'
    },

    eventViews: {},
    initialize: function() {
        this.collection = new TimelineEventCollection()

        // Read events from the DOM using our view class.
        _.each(this.$('.event'), function(el) {
            var view = new TimelineEventView({el: el}).render()
            this.eventViews[view.model.cid] = view
        }, this)

        // Rip the scraped models out of the views to init our collection.
        this.collection.reset(_.pluck(this.eventViews, 'model'))
    },

    fitBounds: function() {
        // Set the bounds of the timeline to the closest years fitting the events.
        this.bounds = {}
        var min = this.bounds.min = new Date(this.collection.first().get("date")),
            max = this.bounds.max = new Date(this.collection.last().get("date"))
        min.setMonth(0)
        min.setDate(1)
        max.setMonth(0)
        max.setDate(1)
        max.setFullYear(this.bounds.max.getFullYear() + 1)
        this.bounds.range = max - min
    },

    position: function(date) {
        // Return the fractional left position of date within the timeline.
        return (date - this.bounds.min) / this.bounds.range
    },

    filter: function(model) {
        // Which events are labeled on the timeline.
        return true
    },

    filterTop: function(model) {
        // Return true to position an event label above the
        // timeline, return false to position an event label below.
        return true
    },

    renderAxis: function() {
        var $axis = this.$('.axis')
        if (!$axis.length) {
            $axis = $('<div>').addClass('axis').appendTo(this.$el)
        }
        $axis.empty()

        var width = $axis.innerWidth(),
            year = new Date(this.bounds.min)
        year.setMonth(0)
        year.setDate(1)
        while (year <= this.bounds.max) {
            var $label = $('<div>')
            $label
                .addClass('label year')
                .text(year.getFullYear())
                .appendTo($axis)
            $label.css('left', (width - $label.width()) * this.position(year))
            year.setFullYear(year.getFullYear() + 1)
        }
    },

    render: function() {
        this.$el.addClass('timeline')

        this.fitBounds()
        this.renderAxis()

        var events = this.collection.toArray(),
            xmax = this.$el.width(),
            // The next available position for a label on the timeline.
            xpos = {'top': 0, 'bottom': 0},
            // Abstract representation of the labels that have been positioned.
            rows = {'top': [[]], 'bottom': [[]]},
            iterCount = events.length

        // While there are still event labels to be placed, iterate over each
        // event trying to fit it into the next available space on the
        // timeline.
        while (events.length && iterCount > 0) {
            var oldpos = _.clone(xpos)
            events = _.reject(events, function(model) {
                var view = this.eventViews[model.cid],
                    side = this.filterTop(model) ? 'top' : 'bottom',
                    posFrac = this.position(model.get('date')),
                    dotLeft = Math.round(posFrac * xmax),
                    labelWidth = view.labelWidth(),
                    // Negatively offset event labels that would bleed off
                    // the right side.
                    contentOffset = Math.min(0, xmax - (dotLeft + labelWidth)),
                    contentLeft = dotLeft + contentOffset

                view.positionDot(100 * posFrac + '%')
                if (!this.filter(model)) {
                    // Filtered out labels are positioned naively and don't
                    // take up space.
                    rows[side][0].push({'view': view, 'offset': contentOffset})
                    return true
                } else if (contentLeft >= xpos[side] && contentLeft + labelWidth <= xmax) {
                    rows[side][0].push({'view': view, 'offset': contentOffset})
                    xpos[side] = contentLeft + labelWidth
                    return true
                }
            }, this)

            _.each(xpos, function(value, side) {
                // If no timeline labels fit (we couldn't advance the xpos),
                // advance to the next row.
                if (value > 0 && value == oldpos[side]) {
                    xpos[side] = 0
                    rows[side].unshift([])
                }
            })

            iterCount--
        }

        // Position the event labels from the abstract representation.
        _.each(rows, function(sideRows, side) {
            _.each(_.reject(sideRows, _.isEmpty), function(row, idx) {
                _.each(row, function(info) {
                    info['view'].positionLabel(this.rowHeight * idx, info['offset'], sideRows.length - idx, side)
                }, this)
            }, this)
        }, this)

        // Scale the timeline parent element to fit the labels.
        this.$el.css({
            'margin-top': this.rowHeight * rows['top'].length,
            'margin-bottom': this.rowHeight * rows['bottom'].length
        })

        return this
    },

    focusEvent: function() {
        this.$el.addClass('focusing')
    },

    unfocusEvent: function() {
        this.$el.removeClass('focusing')
    }
})
