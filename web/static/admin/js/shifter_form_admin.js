(function($) {
    $(document).ready(function() {
        console.log("Shifter Form Admin JS loaded");

        function updateFormIndex(form, index) {
            form.find(':input').each(function() {
                var name = $(this).attr('name');
                if (name) {
                    name = name.replace(/\d+/, index);
                    var id = 'id_' + name;
                    $(this).attr({'name': name, 'id': id});
                }
            });
            form.find('label').each(function() {
                var forAttr = $(this).attr('for');
                if (forAttr) {
                    var newFor = forAttr.replace(/\d+/, index);
                    $(this).attr('for', newFor);
                }
            });
            return form;
        }

        function addStatModifierForm() {
            var formsetContainer = $('#stat_modifiers-group');
            var forms = formsetContainer.find('.dynamic-form');
            var newForm = forms.last().clone(true);
            var formCount = forms.length;
            newForm = updateFormIndex(newForm, formCount);
            newForm.find(':input').val('');  // Clear input values
            forms.last().after(newForm);
            console.log("New form added, total forms:", formCount + 1);
        }

        function deleteStatModifierForm(button) {
            var formToRemove = $(button).closest('.dynamic-form');
            formToRemove.remove();
            console.log("Form removed, total forms:", $('#stat_modifiers-group .dynamic-form').length);
        }

        function collectStatModifiers() {
            var statModifiers = {};
            $('.dynamic-form').each(function(index) {
                var stat = $(this).find('input[name$="-stat_name"]').val();
                var value = $(this).find('input[name$="-modifier"]').val();
                if (stat && value) {
                    statModifiers[stat] = parseInt(value);
                }
            });
            return JSON.stringify(statModifiers);
        }

        // Bind click event to the add button
        $(document).on('click', '.add-form-row', function(e) {
            e.preventDefault();
            addStatModifierForm();
        });

        // Bind click event to the delete buttons
        $(document).on('click', '.delete-form-row', function(e) {
            e.preventDefault();
            deleteStatModifierForm(this);
        });

        // Bind submit event to the form
        $('form').on('submit', function(e) {
            var statModifiersJson = collectStatModifiers();
            $('#id_stat_modifiers').val(statModifiersJson);
        });
    });
})(django.jQuery);