(function() {
    var Message;
    Message = function(arg) {
        this.text = arg.text, this.message_side = arg.message_side;
        this.draw = function(_this) {
            return function() {
                var $message;
                // clone the template from the index page
                $message = $($('.message_template').clone().html());
                $message.addClass(_this.message_side).find('.text').html(_this.text);
                $('.messages').append($message);
                return setTimeout(function() {
                    return $message.addClass('appeared');
                }, 0);
            };
        }(this);
        return this;
    };

    $(function() {
        getMessageText = function() {
            var $message_input;
            $message_input = $('.message_input');
            return $message_input.val();
        };
        // message_side can either be 'left' (bot) or 'right' (user)
        putNewMessage = function(text, message_side) {
            var $messages, message;
            if (typeof text === 'string' && text.trim() === '') {
                return;
            }
            $('.message_input').val('');
            $messages = $('.messages');
            message = new Message({
                text: text,
                message_side: message_side
            });
            message.draw();

            return $messages.animate({
                scrollTop: $messages.prop('scrollHeight')
            }, 300);
        };

        queryServer = function(text) {
            // encode characters such as ? ^ and so on
            encoded_text = $.param({
                question: text
            });

            $.getJSON('query?' + encoded_text, function(result) {
                message_answer = result.answer;
                $('#session').text(message_answer['sessionId']);
                attachments = message_answer.attachments;
                if (result.optional != undefined){ // add the optional only if it exists
                    attachments = attachments.concat(result.optional.attachments);
                }
                for (i=0; i< attachments.length; i++){
                    let attachment = attachments[i]
                    setTimeout(function(){
                        putNewMessage(parse(attachment), 'left');
                    }, i*100);
                };
            });
        }

        // lazy mode
        updateLazymode = function(text){
            var data_text = localStorage.getItem('queries');
            var data = null;
            if (data_text === null){
                data = {list: []};
            } else {
                data = JSON.parse(data_text);
            }

            if (data.list.indexOf(text) === -1){
                data.list.push(text);
                $('#lazy_mode_select').append('<option>' + text + '</option>');
                localStorage.setItem('queries', JSON.stringify(data));
            }
        }

        reloadLaziness = function(){
            var data_text = localStorage.getItem('queries');
            var data = null;
            if (data_text === null){
                data = {list: []};
            } else {
                data = JSON.parse(data_text);
            }

            data.list.forEach(function(element){
                $('#lazy_mode_select').append('<option>' + element + '</option>');
            });
        }

        sendMessage = function() {
            text = getMessageText();
            if (text.trim() === '') {
                return;
            }
            updateLazymode(text);
            queryServer(text);
            return putNewMessage(text, 'right');
        }


        $('.send_message').click(function(e) {
            sendMessage();
        });
        $('.message_input').keyup(function(e) {
            if (e.which === 13) {
                sendMessage();
            }
        });

        reloadLaziness();

        $('#lazy_mode_select').change(function(e){
            if(this.value === 'reset'){
                localStorage.removeItem('queries');
                $('#lazy_mode_select').html('<option>---</option><option>reset</option>');
            } else if(this.value != '---'){
                $('.message_input').val(this.value);
                sendMessage();
                $('#lazy_mode_select').val("---");
            }
        });


        queryServer(':hello');
    });
}.call(this));
