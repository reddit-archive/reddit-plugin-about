var baseURL = 'http://postcards.redditstatic.com/',
    mapURL = _.template('http://maps.google.com/?q=<%= d.lat %>,<%= d.long %>'),
    mapImageURL = _.template('http://maps.googleapis.com/maps/api/staticmap?zoom=<%= d.zoom %>&size=<%= d.width %>x<%= d.height %>&sensor=false&markers=size:mid%7Ccolor:red%7C<%= d.lat %>,<%= d.long %>'),
    redditButtonURL = _.template('http://www.reddit.com/static/button/button2.html?sr=postcards&url=<%= d.url %>')

Postcard = Backbone.Model.extend({})
PostcardsPlaceholder = Backbone.Model.extend({})

PostcardCollection = Backbone.Collection.extend({
    model: Postcard,
    url: baseURL + 'postcards-latest.js',
    chunkSize: null,
    loadedChunks: {},

    load: function(callback) {
        this.fetch({success: _.bind(function(collection, response) {
            this.chunkSize = response.postcards.length
            this.totalCount = response.total_postcard_count
            this.chunkIndex = response.index
            this.chunkCount = _.size(this.chunkIndex)

            var minId = collection.min(function(m) { return m.id }).id
            _.each(this.chunkIndex, function(bounds, idx) {
                // The initial fetch gives us the latest N postcards.
                // We need to skip any chunks we already have.
                bounds[1] = Math.min(minId, bounds[1])
                if (bounds[1] > bounds[0]) {
                    this.add(new PostcardsPlaceholder({
                        chunkStart: bounds[0],
                        chunkEnd: bounds[1],
                        id: 'chunk'+idx
                    }))
                }
            }, this)
            callback()
        }, this)})
    },

    ensureLoaded: function(cardId, callback) {
        if (this.get(cardId)) {
            if (callback) {
                callback()
            }
        }

        var chunkId
        for (var i = 0; i < this.chunkCount; i++) {
            var bounds = this.chunkIndex[i]
            if (cardId >= bounds[0] && cardId <= bounds[1]) {
                chunkId = i
                break
            }
        }
        if (chunkId == null) {
            // :(
            return
        }

        if (chunkId in this.loadedChunks) {
            if (callback) {
                callback()
            }
        } else {
            this.fetch({chunk: chunkId, success: callback})
        }
    },

    fetch: function(options) {
        if (options && 'chunk' in options) {
            options.url = baseURL + 'postcards' + options.chunk + '.js'
            options.add = true
        }
        var success = options.success
        options.success = function(collection, response) {
            if (response.chunk_id) {
                collection.loadedChunks[response.chunk_id] = true
            }
            if (success) { success(collection, response) }
        }
        Backbone.Collection.prototype.fetch.call(this, options)
    },

    sync: function(method, model, options) {
        Backbone.sync(method, model, _.extend({
            dataType: 'jsonp',
            jsonp: false,
            jsonpCallback: 'postcardCallback' + ('chunk' in options ? options.chunk : ''),
            cache: true
        }, options))
    },

    parse: function(response) {
        return response.postcards
    },

    comparator: function(model) {
        return model instanceof Postcard ? -model.id : -model.get('chunkStart')
    }
})

PostcardRouter = Backbone.Router.extend({
    routes: {
        'view/:cardId': 'viewCard',
        'view/:cardId/:side': 'viewCard'
    },

    initialize: function(options) {
        this.zoomer = options.zoomer
        this.zoomer.on('showcard', function(cardId, side) {
            this.navigate('view/' + cardId + '/' + side, {replace: true})
        }, this)
        this.zoomer.on('hidecard', function(cardId) {
            this.navigate('browse', {replace: true})
        }, this)
    },

    viewCard: function(cardId, side) {
        this.zoomer.zoomById(Number(cardId), side)
    }
})

var PostcardOverlayView = Backbone.View.extend({
    tagName: 'div',
    distanceThreshold: 10,

    initialize: function() {
        this.options.parent.bind('showcard', this._position, this)
        this.options.parent.bind('hidecard', this.hide, this)
        this.currentTarget = {left: 0, top: 0}
        this.$el.addClass('postcard-overlay')
    },

    hide: function() {
        this.$el.addClass('hide')
    },

    _position: function() {
        var oldTarget = this.currentTarget,
            target = this._target()

        var distance = Math.sqrt(Math.pow(target.left - oldTarget.left, 2) + Math.pow(target.top - oldTarget.top, 2))
        if (distance >= this.distanceThreshold) {
            this.hide()
            this.$el.css(target)
            this.currentTarget = target
            _.delay(_.bind(function() {
                $(this.el)
                    .removeClass('hide')
                    .addClass('show')
            }, this), Modernizr.csstransforms3d ? 500 : 0)
       }
    }
})

var PostcardInfoView = PostcardOverlayView.extend({
    className: 'infobox',

    events: {
        'mouseover': 'zoomIn',
        'mouseout': 'zoomOut'
    },

    render: function() {
        this.$el.append(
            this.make('a', {'class': 'maplink', target: '_blank'}, [
                this.make('img', {'class': 'map'})
            ]),
            this.make('span', {'class': 'date'})
        )

        this.zoomOut()
        this.$('.date').text(this.model.get('date'))
        return this
    },

    zoomIn: function() {
        this.updateMap(8)
    },

    zoomOut: function() {
        this.updateMap(1)
    },

    updateMap: function(zoom) {
        this.$('.maplink').attr('href', mapURL({
            lat: this.model.get('latitude'),
            'long': this.model.get('longitude')
        }))
        this.$('.map').attr('src', mapImageURL({
            lat: this.model.get('latitude'),
            'long': this.model.get('longitude'),
            width: 85,
            height: 85,
            zoom: zoom
        }))
    },

    _target: function() {
        var parentPos = this.options.parent.currentFacePosition()

        // Since the parent is animating, we must calculate the final position.
        return {
            left: parentPos.left - this.$el.outerWidth() - 10,
            top: parentPos.top
        }
    }
})

var PostcardRedditView = PostcardOverlayView.extend({
    className: 'redditbutton',

    render: function() {
        var iframe = $('<iframe src="'+redditButtonURL({url: window.location})+'">')
        iframe
            .css('opacity', 0)
            .load(function() {
                iframe.css('opacity', 1)
            })
        this.$el.append(iframe)
        return this
    },

    _target: function() {
        var infopos = PostcardInfoView.prototype._target.apply(this)
        infopos.top += 110
        return infopos
    }
})

var PostcardCloseView = PostcardOverlayView.extend({
    className: 'postcard-close',
    distanceThreshold: 0,

    events: {
        'click': 'unzoom'
    },

    unzoom: function(ev) {
        this.options.zoomer.unzoom()
    },

    _target: function() {
        var parentPos = this.options.parent.currentFacePosition()
        return {
            left: parentPos.right,
            top: parentPos.top
        }
    }
})

var PostcardZoomView = Backbone.View.extend({
    tagName: 'div',
    className: 'postcard-zoombox',
    topSpace: 20,

    events: {
        'click .zoom .face': 'flip'
    },

    initialize: function() {
        this.model = this.model || this.options.parent.model

        $(this.el).append(
            this.make('div', {'class': 'zoom'}, [
                this.make('img', {'class': 'face front'}),
                this.make('img', {'class': 'face back'})
            ])
        )

        this.$el.append(new PostcardInfoView({model: this.model, parent: this}).render().el)
        this.$el.append(new PostcardRedditView({parent: this}).render().el)
        this.$el.append(new PostcardCloseView({parent: this, zoomer: this.options.zoomer}).render().el)

        var smallImages = this.model.get('images').small
        var frontOrientation = smallImages.front.width > smallImages.front.height,
            backOrientation = smallImages.back.width > smallImages.back.height
        if (frontOrientation != backOrientation) {
            $(this.el).addClass('rotate')
        }

        this.currentSide = 'front'
    },

    render: function() {
        this._changeSize('small')
        this._scale()
        this._origPosition()
        return this
    },

    currentImages: function() {
        return this.model.get('images')[this.size]
    },

    currentImage: function() {
        return this.currentImages()[this.currentSide]
    },

    currentFacePosition: function() {
        var image = this.currentImage(),
            position = {
                left: this.position.left + (this.maxWidth - image.width) / 2,
                top: this.position.top + (this.maxHeight - image.height) / 2
            }
        position.right = position.left + image.width
        position.bottom = position.top + image.height
        return position
    },

    _origPosition: function() {
        var pos = this.options.parent.$('img').offset()
        this.$('.zoom').css({
            left: pos.left - this.frontLeft,
            top: pos.top - this.frontTop
        })
    },

    _changeSize: function(size) {
        this.size = size
        var images = this.currentImages()

        // Scale and center the images.
        this.maxWidth = Math.max(images.front.width, images.back.width),
        this.maxHeight = Math.max(images.front.height, images.back.height)
        this.frontLeft = (this.maxWidth - images.front.width) / 2,
        this.frontTop = (this.maxHeight - images.front.height) / 2
    },

    _scale: function(size, keepImages) {
        var images = this.currentImages()

        // Scale and displace the .zoom plane to match the front face.
        this.$('.zoom').css({
            width: images.front.width,
            height: images.front.height,
            marginLeft: this.frontLeft,
            marginTop: this.frontTop
        })

        this.$('.front')
            .attr('width', images.front.width)
            .attr('height', images.front.height)


        // Center the back face with respect to the front.
        this.$('.back')
            .attr('width', images.back.width)
            .attr('height', images.back.height)
            .css({
                left: (images.front.width - images.back.width) / 2,
                top: (images.front.height - images.back.height) / 2
            })

        if (!keepImages) {
            this.$('.front').attr('src', baseURL + images.front.filename)
            this.$('.back').attr('src', baseURL + images.back.filename)
        }
    },

    flip: function() {
        if (!this.$el.is('.zoomed')) { return }
        this.$el.toggleClass('flipped')
        this.currentSide = this.$el.is('.flipped') ? 'back' : 'front'
        this.trigger('flip', this.currentSide)
        this.trigger('showcard')
        return this
    },

    zoom: function() {
        this._changeSize('full')
        this.position = {
            'left': ($(window).width() - this.maxWidth) / 2,
            'top': Math.max(this.$el.parent().position().top + this.topSpace,
                            $(window).scrollTop() + ($(window).height() - this.maxHeight) / 2)
        }
        this.$('.zoom').css(this.position)
        this._scale()
        this.$el.addClass('zoomed')
        this.trigger('showcard')
        return this
    },

    unzoom: function() {
        this.trigger('hidecard')
        this._changeSize('small')
        this._origPosition()
        this._scale(true)
        this.$el.removeClass('flipped zoomed')
        _.delay(_.bind(function() {
            this.unbind()
            this.remove()
        }, this), Modernizr.csstransforms3d ? 700 : 0)
    }
})

var PostcardView = Backbone.View.extend({
    tagName: 'div',
    className: 'postcard',

    events: {
        'click img': 'zoom'
    },

    render: function() {
        var thumb = this.model.get('images').small,
            front = thumb.front || {}
        this.$el
            .append(
                $(this.make('img', {
                    src: baseURL + front.filename,
                    width: front.width,
                    height: front.height
                })).css('margin-top', -front.height / 2))
            .addClass('postcard-'+this.model.id)
        return this
    },

    zoom: function() {
        this.options.zoomer.zoom(this)
    }
})

var PostcardsPlaceholderView = Backbone.View.extend({
    tagName: 'div',
    className: 'placeholder',
    perLine: 4,
    lineHeight: 215 + 2 * 4,

    render: function() {
        var grid = this.options.parent
        this.$el
            .css('height', Math.ceil(grid.collection.chunkSize / this.perLine) * this.lineHeight)
            .addClass('placeholder-'+this.model.id)
        return this
    }
})

var PostcardGridView = Backbone.View.extend({
    initialize: function() {
        this.collection
            .on('add', this.addOne, this)
            .on('remove', this.removeOne, this)
            .on('reset', this.addAll, this)

        this.itemViews = []
        this.placeholders = []

        _.bindAll(this, '_clickOut', '_scroll')
        $('body').bind('click', this._clickOut)
        $(window).bind('scroll', this._scroll)
    },

    addOne: function(model) {
        if (model instanceof Postcard) {
            var view = new PostcardView({model: model, zoomer: this})
        } else if (model instanceof PostcardsPlaceholder) {
            var view = new PostcardsPlaceholderView({model: model, parent: this})
            this.placeholders.push(view)
        }

        var index = this.collection.indexOf(model),
            elBefore = this.$el.children().eq(index - 1)
        if (elBefore.length) {
            elBefore.after(view.render().el)
        } else {
            this.$el.append(view.render().el)
        }
        this.itemViews[model.id] = view
    },

    removeOne: function(model) {
        var view = this.itemViews[model.id]
        view.remove()
        this.itemViews[model.id] = null
    },

    addAll: function() {
        this.collection.each(this.addOne, this)

        // Ensure the viewport is full of postcards after collection load.
        _.defer(this._scroll)
    },

    zoomById: function(cardId, side) {
        this.collection.ensureLoaded(cardId, _.bind(function() {
            var postcardView = this.itemViews[cardId]
            if (postcardView) {
                $(window).scrollTop(postcardView.$el.offset().top - $(window).height() / 2)
                this._scroll()
                this.zoom(postcardView, side)
            }
        }, this))
    },

    zoom: function(postcard, side) {
        side = side || 'back'
        if (!this.currentZoom || postcard.model.id != this.currentZoom.model.id) {
            this.unzoom(true)
            this.zoomScroll = $(window).scrollTop()
            this.$el.addClass('zoomed')
            var zoom = this.currentZoom = new PostcardZoomView({parent: postcard, zoomer: this})
            zoom.on('flip', this.onFlip, this)
            $('#about-postcards').append(zoom.render().el)

            // Defer to position the zoom before we start moving it.
            _.defer(_.bind(function() {
                zoom.zoom()
                if (side == 'back') {
                    zoom.flip()
                }
                this.trigger('showcard', postcard.model.id, side)
            }, this))
        } else if (this.currentZoom.currentSide != side) {
            this.currentZoom.flip()
        }
    },

    unzoom: function(switching) {
        if (!switching) {
            this.$el.removeClass('zoomed')
            this.trigger('hidecard')
        }
        if (this.currentZoom) {
            this.currentZoom.unzoom()
            this.currentZoom.off('flip', this.onFlip, this)
            this.currentZoom = null
        }
    },

    onFlip: function(side) {
        this.trigger('showcard', this.currentZoom.model.id, side)
    },

    _clickOut: function(ev) {
        if (this.currentZoom && !$(ev.target).closest($([this.currentZoom.el, this.currentZoom.options.parent.el])).length) {
            this.unzoom()
        }
    },

    _scroll: _.throttle(function() {
        var unzoomThreshold = 800,
            scrollTop = $(window).scrollTop()
        if (this.currentZoom && Math.abs(this.zoomScroll - scrollTop) > unzoomThreshold) {
            this.unzoom()
        }

        this.placeholders = _.reject(this.placeholders, function(placeholder) {
            var pos = placeholder.$el.offset(),
                height = placeholder.$el.height()
            if (Math.abs(scrollTop - pos.top) < height + $(window).height() ) {
                var model = placeholder.model
                this.collection.ensureLoaded(model.get('chunkStart'), _.bind(function() {
                    this.collection.remove(model)
                }, this))
                return true
            }
        }, this)
    }, 250)
})

r.about.pages['about-postcards'] = function() {
    $('.abouttitle h1').hide()

    postcards = new PostcardCollection
    var grid = new PostcardGridView({
        el: $('#postcards'),
        collection: postcards
    })

    var cardRouter = new PostcardRouter({zoomer: grid})
    postcards.load(function() {
        if (!Backbone.history.start()) {
            cardRouter.navigate('browse')
        }
        $('.abouttitle h1')
            .find('.count').text(postcards.totalCount).end()
            .fadeIn(100)
    })
}
